/**
 * k6 併發結帳壓力測試
 *
 * 模擬多個用戶同時搶購庫存有限的商品，驗證悲觀鎖的正確性。
 *
 * 執行方式：
 *   k6 run --vus 100 checkout_stress.js
 *   k6 run --vus 500 checkout_stress.js
 */

import http from "k6/http";
import { check } from "k6";
import { Counter, Trend } from "k6/metrics";
import { SharedArray } from "k6/data";

// --- Custom Metrics ---
const checkoutSuccess = new Counter("checkout_success");
const checkoutStockError = new Counter("checkout_stock_error");
const checkoutOtherError = new Counter("checkout_other_error");
const checkoutDuration = new Trend("checkout_duration", true); // in ms

// --- Load users from seed output ---
const users = new SharedArray("users", function () {
  return JSON.parse(open("./users.json"));
});

// --- k6 Options ---
// VU count is set via CLI: k6 run --vus N
export const options = {
  scenarios: {
    checkout: {
      executor: "per-vu-iterations",
      vus: __ENV.VUS ? parseInt(__ENV.VUS) : 100,
      iterations: 1,
      maxDuration: "120s",
    },
  },
  // No thresholds — we check in handleSummary
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  const vuIndex = __VU - 1; // VU is 1-based
  if (vuIndex >= users.length) {
    console.warn(`VU ${__VU} exceeds user count (${users.length}), skipping`);
    return;
  }

  const user = users[vuIndex];

  const payload = JSON.stringify({
    recipient_name: `Test User ${vuIndex}`,
    recipient_phone: "0912345678",
    shipping_address: `Test Address ${vuIndex}, Test City, 12345`,
    payment_method: "COD",
  });

  const params = {
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${user.token}`,
    },
    timeout: "60s",
  };

  const start = Date.now();
  const res = http.post(`${BASE_URL}/api/v1/orders/checkout`, payload, params);
  const duration = Date.now() - start;

  checkoutDuration.add(duration);

  if (res.status === 201) {
    checkoutSuccess.add(1);
  } else if (res.status === 400) {
    // Stock insufficient or empty cart
    checkoutStockError.add(1);
  } else {
    checkoutOtherError.add(1);
    console.error(
      `VU ${__VU} (${user.email}): status=${res.status} body=${res.body}`
    );
  }

  check(res, {
    "status is 201 or 400": (r) => r.status === 201 || r.status === 400,
  });
}

export function handleSummary(data) {
  const success =
    data.metrics.checkout_success?.values?.count || 0;
  const stockErr =
    data.metrics.checkout_stock_error?.values?.count || 0;
  const otherErr =
    data.metrics.checkout_other_error?.values?.count || 0;

  const duration = data.metrics.checkout_duration?.values || {};
  const vus =
    data.metrics.vus_max?.values?.value ||
    options.scenarios.checkout.vus;

  const expectedSuccess = parseInt(__ENV.EXPECTED_SUCCESS || "10");
  const integrityPass = success === expectedSuccess;

  const result = {
    vus: vus,
    expected_success: expectedSuccess,
    checkout_success: success,
    checkout_stock_error: stockErr,
    checkout_other_error: otherErr,
    inventory_integrity: integrityPass ? "PASS" : "FAIL",
    duration_ms: {
      avg: Math.round(duration.avg || 0),
      min: Math.round(duration.min || 0),
      med: Math.round(duration["med"] || 0),
      p90: Math.round(duration["p(90)"] || 0),
      p95: Math.round(duration["p(95)"] || 0),
      p99: Math.round(duration["p(99)"] || 0),
      max: Math.round(duration.max || 0),
    },
  };

  const summary = `
╔══════════════════════════════════════════════════╗
║         Checkout Stress Test Results             ║
╠══════════════════════════════════════════════════╣
║  VUs:                ${String(vus).padStart(6)}                       ║
║  Expected Success:   ${String(expectedSuccess).padStart(6)}                       ║
║  ─────────────────────────────────────────────── ║
║  ✓ Checkout Success: ${String(success).padStart(6)}                       ║
║  ✗ Stock Error:      ${String(stockErr).padStart(6)}                       ║
║  ✗ Other Error:      ${String(otherErr).padStart(6)}                       ║
║  ─────────────────────────────────────────────── ║
║  Inventory Integrity: ${(integrityPass ? "PASS ✓" : "FAIL ✗").padEnd(6)}                      ║
║  ─────────────────────────────────────────────── ║
║  Duration (ms):                                  ║
║    avg=${String(result.duration_ms.avg).padStart(6)}  p50=${String(result.duration_ms.med).padStart(6)}  p90=${String(result.duration_ms.p90).padStart(6)}    ║
║    p95=${String(result.duration_ms.p95).padStart(6)}  p99=${String(result.duration_ms.p99).padStart(6)}  max=${String(result.duration_ms.max).padStart(6)}    ║
╚══════════════════════════════════════════════════╝
`;

  return {
    stdout: summary,
    "results.json": JSON.stringify(result, null, 2),
  };
}
