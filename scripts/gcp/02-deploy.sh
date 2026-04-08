#!/bin/bash
# =============================================================================
# 02-deploy.sh — 應用程式部署腳本
#
# 用途：每次發布新版本時執行
#   1. 建置並推送 Docker Image 至 Artifact Registry
#   2. 部署/更新 Cloud Run
#   3. 更新 GCE VM 上的 Celery Worker
#   4. 建立或更新 Cloud Scheduler 排程任務
#
# 執行方式：
#   cd scripts/gcp
#   bash 02-deploy.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"
source "${SCRIPT_DIR}/vm/.env"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# 取得 backend/ 目錄路徑（相對於 scripts/gcp/）
BACKEND_DIR="${SCRIPT_DIR}/../../backend"

# =============================================================================
# 1. 設定 Docker 認證（Artifact Registry）
# =============================================================================
log "設定 Artifact Registry 認證..."
gcloud auth configure-docker "asia-east1-docker.pkg.dev" --quiet

# =============================================================================
# 2. 建置 Docker Image
# =============================================================================
log "建置 Docker Image..."
docker build \
  --platform linux/amd64 \
  -t "${IMAGE_FULL}:latest" \
  -t "${IMAGE_FULL}:$(git -C "${BACKEND_DIR}/.." rev-parse --short HEAD)" \
  "${BACKEND_DIR}"

# =============================================================================
# 3. 推送至 Artifact Registry
# =============================================================================
log "推送 Docker Image..."
docker push "${IMAGE_FULL}:latest"
docker push "${IMAGE_FULL}:$(git -C "${BACKEND_DIR}/.." rev-parse --short HEAD)"

# =============================================================================
# 4. 部署 Cloud Run
#
# 設計原因：
#   --add-cloudsql-instances 讓 Cloud Run 透過 Cloud SQL Auth Proxy（內建）
#   以 Unix Socket 連線資料庫，不需要 IP 或密碼傳輸，完全 IAM 認證。
#
#   DB_HOST 設定為 /cloudsql/CONNECTION_NAME，asyncpg 透過 ?host= 參數
#   支援 Unix Socket 連線（config.py 中的 database_url 會自動處理）。
#
#   --vpc-connector 讓 Cloud Run 能透過內網存取 GCE VM 上的 Redis。
#
#   Secrets 透過 --set-secrets 注入為環境變數，Cloud Run 在啟動時
#   自動從 Secret Manager 讀取最新版本，不需要在程式碼中處理。
# =============================================================================
log "部署 Cloud Run..."

# 取得 VM 內部 IP（設定 REDIS_URL 用）
VM_INTERNAL_IP=$(gcloud compute instances describe "${VM_NAME}" \
  --zone="${ZONE}" \
  --format="value(networkInterfaces[0].networkIP)" \
  --project="${PROJECT_ID}")

if [ -z "${FRONTEND_URL:-}" ]; then
  echo "ERROR: vm/.env 中 FRONTEND_URL 未設定，請填入 Vercel 部署網址後重新執行。" >&2
  exit 1
fi

gcloud run deploy "${CLOUD_RUN_SERVICE}" \
  --image="${IMAGE_FULL}:latest" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8080 \
  --min-instances=0 \
  --max-instances=3 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --service-account="${SA_CLOUD_RUN}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --vpc-connector="${VPC_CONNECTOR}" \
  --add-cloudsql-instances="${CLOUD_SQL_CONNECTION_NAME}" \
  --set-env-vars="\
ENV=production,\
PROJECT_NAME=E-commerce Backend,\
ALGORITHM=HS256,\
ACCESS_TOKEN_EXPIRE_MINUTES=1440,\
REFRESH_TOKEN_EXPIRE_DAYS=30,\
BREVO_SENDER_EMAIL=clocklife0226@gmail.com,\
BREVO_SENDER_NAME=cyWeb,\
FRONTEND_URL=${FRONTEND_URL},\
AWS_S3_BUCKET=cy-ecommerce-bucket,\
AWS_S3_REGION=ap-northeast-1,\
GUEST_TOKEN_COOKIE_NAME=guest_cart_token,\
GUEST_TOKEN_MAX_AGE=604800,\
GUEST_TOKEN_PATH=/api/cart,\
GUEST_TOKEN_SECURE=true,\
GUEST_TOKEN_SAMESITE=none,\
REDIS_URL=redis://${VM_INTERNAL_IP}:6379/0,\
DB_USER=${CLOUD_SQL_USER},\
DB_HOST=/cloudsql/${CLOUD_SQL_CONNECTION_NAME},\
DB_PORT=5432,\
DB_NAME=${CLOUD_SQL_DB},\
DOCS_URL=,\
REDOC_URL=" \
  --set-secrets="\
DB_PASSWORD=db-password:latest,\
SECRET_KEY=jwt-secret-key:latest,\
BREVO_API_KEY=brevo-api-key:latest,\
AWS_ACCESS_KEY_ID=aws-access-key-id:latest,\
AWS_SECRET_ACCESS_KEY=aws-secret-access-key:latest,\
CLEANUP_API_KEY=cleanup-api-key:latest" \
  --project="${PROJECT_ID}"

# 取得 Cloud Run URL
CLOUD_RUN_URL=$(gcloud run services describe "${CLOUD_RUN_SERVICE}" \
  --region="${REGION}" \
  --format="value(status.url)" \
  --project="${PROJECT_ID}")

log "Cloud Run 部署完成：${CLOUD_RUN_URL}"

# =============================================================================
# 5. 更新 GCE VM 上的 Celery Worker
#
# 設計原因：
#   Celery Worker 需要最新的 Image 才能執行最新版本的任務。
#   docker compose pull + up -d 會在不中斷 Redis 的情況下滾動更新 Worker。
# =============================================================================
log "更新 GCE VM 上的 Celery Worker..."
gcloud compute ssh "${VM_NAME}" \
  --zone="${ZONE}" \
  --project="${PROJECT_ID}" \
  --command="cd ${VM_WORKDIR} && \
    sudo docker compose pull celery-worker && \
    sudo docker compose up -d celery-worker && \
    echo 'Celery Worker 更新完成'"

# =============================================================================
# 6. Cloud Scheduler — 每月清理排程
#
# 設計原因：
#   原本的 Celery Beat 只有一個排程任務（刪除過期帳號）。
#   以目前的規模，每月執行一次已足夠。
#   用 Cloud Scheduler 直接呼叫 Cloud Run HTTP endpoint 更簡潔，
#   不需要維護額外的 Beat 進程。
#   OIDC 認證確保只有 Scheduler 能呼叫此 endpoint。
# =============================================================================
log "設定 Cloud Scheduler..."

CLEANUP_API_KEY=$(gcloud secrets versions access latest \
  --secret="cleanup-api-key" \
  --project="${PROJECT_ID}" 2>/dev/null || echo "CHANGE_ME")

if ! gcloud scheduler jobs describe "${SCHEDULER_JOB}" \
    --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud scheduler jobs create http "${SCHEDULER_JOB}" \
    --location="${REGION}" \
    --schedule="0 0 1 * *" \
    --time-zone="Asia/Taipei" \
    --uri="${CLOUD_RUN_URL}/internal/cleanup/expired-accounts" \
    --http-method=POST \
    --headers="X-Cleanup-Api-Key=${CLEANUP_API_KEY}" \
    --oidc-service-account-email="${SA_SCHEDULER}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --oidc-token-audience="${CLOUD_RUN_URL}" \
    --attempt-deadline=120s \
    --project="${PROJECT_ID}"
  log "Cloud Scheduler 建立完成（每月 1 日 00:00 Asia/Taipei）。"
else
  # 更新現有排程（URL 可能因重新部署而改變）
  gcloud scheduler jobs update http "${SCHEDULER_JOB}" \
    --location="${REGION}" \
    --uri="${CLOUD_RUN_URL}/internal/cleanup/expired-accounts" \
    --headers="X-Cleanup-Api-Key=${CLEANUP_API_KEY}" \
    --project="${PROJECT_ID}"
  log "Cloud Scheduler 更新完成。"
fi

# =============================================================================
# 完成
# =============================================================================
echo ""
echo -e "${GREEN}===== 部署完成 =====${NC}"
echo ""
echo "Cloud Run URL：${CLOUD_RUN_URL}"
echo ""
echo "驗證步驟："
echo "  1. 測試 API：curl ${CLOUD_RUN_URL}/api/health"
echo "  2. 手動觸發 Scheduler 測試清理 API："
echo "     gcloud scheduler jobs run ${SCHEDULER_JOB} --location=${REGION}"
echo "  3. 確認 Vercel 前端環境變數：VITE_API_BASE_URL=${CLOUD_RUN_URL}"