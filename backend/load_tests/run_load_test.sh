#!/usr/bin/env bash
#
# 自動化多輪併發搶購壓力測試
#
# 用法：
#   ./run_load_test.sh                    # 預設等級: 100,300,500,800,1000,1500,2000
#   ./run_load_test.sh "100,500,1000"     # 自訂等級
#   STOCK=20 ./run_load_test.sh "100"     # 自訂庫存數量
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LEVELS="${1:-100,300,500,800,1000,1500,2000}"
STOCK="${STOCK:-10}"
CONTAINER="ecommerce_api"
BASE_URL="${BASE_URL:-http://localhost:8000}"
RESULTS_DIR="${SCRIPT_DIR}/results"

mkdir -p "$RESULTS_DIR"

# macOS: 提高檔案描述符限制
ulimit -n 10240 2>/dev/null || true

echo "============================================"
echo "  Checkout Stress Test Runner"
echo "============================================"
echo "  Stock:     $STOCK"
echo "  Levels:    $LEVELS"
echo "  Base URL:  $BASE_URL"
echo "  Results:   $RESULTS_DIR"
echo "============================================"
echo ""

IFS=',' read -ra VU_LIST <<< "$LEVELS"

for VUS in "${VU_LIST[@]}"; do
    VUS=$(echo "$VUS" | tr -d ' ')
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Round: ${VUS} VUs (stock=${STOCK})"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 1. Seed data (create users on first round, reset-only on subsequent)
    if [ "$VUS" = "${VU_LIST[0]}" ]; then
        echo "[1/3] Seeding ${VUS} users + product (stock=${STOCK})..."
        docker exec "$CONTAINER" python -m load_tests.seed_load_test \
            --num-users "$VUS" --stock "$STOCK"
    else
        # 如果需要更多用戶，重新建立；否則只重置
        PREV_MAX=0
        for prev in "${VU_LIST[@]}"; do
            prev=$(echo "$prev" | tr -d ' ')
            if [ "$prev" = "$VUS" ]; then break; fi
            if [ "$prev" -gt "$PREV_MAX" ]; then PREV_MAX=$prev; fi
        done

        if [ "$VUS" -gt "$PREV_MAX" ]; then
            echo "[1/3] Seeding ${VUS} users + resetting product (stock=${STOCK})..."
            docker exec "$CONTAINER" python -m load_tests.seed_load_test \
                --num-users "$VUS" --stock "$STOCK"
        else
            echo "[1/3] Resetting product (stock=${STOCK}) and carts for ${VUS} users..."
            docker exec "$CONTAINER" python -m load_tests.seed_load_test \
                --num-users "$VUS" --stock "$STOCK" --reset-only
        fi
    fi

    # 2. Copy users.json from container
    echo "[2/3] Copying users.json from container..."
    docker cp "${CONTAINER}:/app/load_tests/users.json" "${SCRIPT_DIR}/users.json"

    # 3. Run k6 (from SCRIPT_DIR so results.json lands there)
    echo "[3/3] Running k6 with ${VUS} VUs..."
    (cd "$SCRIPT_DIR" && k6 run \
        --env VUS="$VUS" \
        --env BASE_URL="$BASE_URL" \
        --env EXPECTED_SUCCESS="$STOCK" \
        checkout_stress.js) \
        2>&1 | tee "${RESULTS_DIR}/results_${VUS}vu.log"

    # Copy structured results
    if [ -f "${SCRIPT_DIR}/results.json" ]; then
        mv "${SCRIPT_DIR}/results.json" "${RESULTS_DIR}/results_${VUS}vu.json"
    fi

    # Wait between rounds
    echo "Waiting 3 seconds before next round..."
    sleep 3
done

echo ""
echo "============================================"
echo "  All rounds complete!"
echo "  Results saved in: $RESULTS_DIR"
echo "============================================"

# Print summary table
echo ""
echo "  VUs | Success | StockErr | OtherErr | Integrity | p95(ms) | p99(ms)"
echo "  ----|---------|----------|----------|-----------|---------|--------"
for VUS in "${VU_LIST[@]}"; do
    VUS=$(echo "$VUS" | tr -d ' ')
    JSON_FILE="${RESULTS_DIR}/results_${VUS}vu.json"
    if [ -f "$JSON_FILE" ]; then
        # Parse with python (available in most systems)
        python3 -c "
import json, sys
d = json.load(open('$JSON_FILE'))
print(f\"  {d['vus']:>4} | {d['checkout_success']:>7} | {d['checkout_stock_error']:>8} | {d['checkout_other_error']:>8} | {d['inventory_integrity']:>9} | {d['duration_ms']['p95']:>7} | {d['duration_ms']['p99']:>7}\")
" 2>/dev/null || echo "  ${VUS} | (parse error)"
    else
        echo "  ${VUS} | (no results)"
    fi
done
