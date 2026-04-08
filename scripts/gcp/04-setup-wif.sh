#!/bin/bash
# =============================================================================
# 04-setup-wif.sh — Workload Identity Federation 設定腳本
#
# 用途：建立 WIF Pool/Provider 與 CD Service Account，
#       讓 GitHub Actions 透過 OIDC 認證操作 GCP 資源，無需 SA Key。
# 執行頻率：首次部署時執行一次，可安全重複執行（已存在的資源會跳過）
#
# 執行方式：
#   cd scripts/gcp
#   bash 04-setup-wif.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[INFO]${NC} $1"; }
skip() { echo -e "${YELLOW}[SKIP]${NC} $1 已存在，跳過。"; }

# =============================================================================
# 0. 設定專案與啟用 API
# =============================================================================
log "設定 GCP 專案..."
gcloud config set project "${PROJECT_ID}"

log "啟用 IAM Credentials API..."
gcloud services enable iamcredentials.googleapis.com --project="${PROJECT_ID}"

# =============================================================================
# 1. 建立 CD 專用 Service Account
#
# 設計原因：
#   CD 需要的權限（push image、deploy Cloud Run、IAP tunnel SSH）
#   與 Cloud Run runtime 的權限不同。獨立 SA 遵守最小權限原則。
# =============================================================================
log "建立 CD Service Account..."
if ! gcloud iam service-accounts describe \
    "${SA_CD}@${PROJECT_ID}.iam.gserviceaccount.com" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud iam service-accounts create "${SA_CD}" \
    --display-name="CD Pipeline Service Account" \
    --project="${PROJECT_ID}"
  log "Service Account ${SA_CD} 建立完成。"
else
  skip "Service Account ${SA_CD}"
fi

# 授予 CD SA 所需權限
log "設定 CD Service Account 權限..."

CD_SA_EMAIL="${SA_CD}@${PROJECT_ID}.iam.gserviceaccount.com"

# 推送 Docker image 至 Artifact Registry
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CD_SA_EMAIL}" \
  --role="roles/artifactregistry.writer" --condition=None

# 部署 Cloud Run service
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CD_SA_EMAIL}" \
  --role="roles/run.admin" --condition=None

# Cloud Run 部署時指定 runtime SA
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CD_SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" --condition=None

# 透過 IAP tunnel SSH 至 VM
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CD_SA_EMAIL}" \
  --role="roles/iap.tunnelResourceAccessor" --condition=None

# SSH 登入 VM（OS Login）
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CD_SA_EMAIL}" \
  --role="roles/compute.osLogin" --condition=None

# 讀取 Secret Manager（Cloud Run 部署 --set-secrets 需要驗證 secret 存在）
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CD_SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" --condition=None

# 更新 Cloud Scheduler job
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CD_SA_EMAIL}" \
  --role="roles/cloudscheduler.admin" --condition=None

log "CD Service Account 權限設定完成。"

# =============================================================================
# 2. 建立 Workload Identity Pool
#
# 設計原因：
#   WIF Pool 是 OIDC Provider 的容器，一個專案可有多個 Pool。
#   使用獨立的 Pool 管理 GitHub Actions 的身份對應。
# =============================================================================
log "建立 Workload Identity Pool..."
if ! gcloud iam workload-identity-pools describe "${WIF_POOL}" \
    --location="global" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud iam workload-identity-pools create "${WIF_POOL}" \
    --location="global" \
    --display-name="GitHub Actions Pool" \
    --description="Workload Identity Pool for GitHub Actions CD" \
    --project="${PROJECT_ID}"
  log "Workload Identity Pool 建立完成。"
else
  skip "Workload Identity Pool ${WIF_POOL}"
fi

# =============================================================================
# 3. 建立 OIDC Provider
#
# 設計原因：
#   OIDC Provider 定義如何驗證 GitHub Actions 發出的 JWT token。
#   attribute-mapping 將 GitHub 的 claims 對應到 Google 的 attributes，
#   後續 IAM binding 可用這些 attributes 做條件限制。
# =============================================================================
log "建立 OIDC Provider..."
if ! gcloud iam workload-identity-pools providers describe "${WIF_PROVIDER}" \
    --workload-identity-pool="${WIF_POOL}" \
    --location="global" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud iam workload-identity-pools providers create-oidc "${WIF_PROVIDER}" \
    --workload-identity-pool="${WIF_POOL}" \
    --location="global" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --allowed-audiences="https://iam.googleapis.com/" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --attribute-condition="assertion.repository == '${GITHUB_REPO}'" \
    --project="${PROJECT_ID}"
  log "OIDC Provider 建立完成。"
else
  skip "OIDC Provider ${WIF_PROVIDER}"
fi

# =============================================================================
# 4. 綁定 WIF ↔ Service Account
#
# 設計原因：
#   限定只有指定 GitHub repository 的 workflow 才能取得 CD SA 的 token。
#   使用 principalSet 搭配 attribute.repository 條件，
#   其他 repo 的 workflow 無法冒用此 SA。
# =============================================================================
log "設定 WIF ↔ Service Account binding..."

WIF_POOL_ID=$(gcloud iam workload-identity-pools describe "${WIF_POOL}" \
  --location="global" \
  --project="${PROJECT_ID}" \
  --format="value(name)")

gcloud iam service-accounts add-iam-policy-binding "${CD_SA_EMAIL}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WIF_POOL_ID}/attribute.repository/${GITHUB_REPO}" \
  --project="${PROJECT_ID}"

log "WIF ↔ Service Account binding 設定完成。"

# =============================================================================
# 5. 輸出 GitHub Secrets 設定值
# =============================================================================
WIF_PROVIDER_FULL=$(gcloud iam workload-identity-pools providers describe "${WIF_PROVIDER}" \
  --workload-identity-pool="${WIF_POOL}" \
  --location="global" \
  --project="${PROJECT_ID}" \
  --format="value(name)")

echo ""
echo -e "${GREEN}===== WIF 設定完成 =====${NC}"
echo ""
echo "請至 GitHub Repository Settings → Secrets and variables → Actions"
echo "設定以下 Repository Secrets："
echo ""
echo "  GCP_PROJECT_ID     = ${PROJECT_ID}"
echo "  GCP_WIF_PROVIDER   = ${WIF_PROVIDER_FULL}"
echo "  GCP_CD_SA_EMAIL    = ${CD_SA_EMAIL}"
echo ""
