 #!/bin/bash
# =============================================================================
# 03-setup-vm.sh — GCE VM 初始化腳本
#
# 用途：首次設定 GCE VM，將 Docker Compose 設定與環境變數上傳至 VM
# 執行頻率：VM 首次建立後執行一次，或需要更新 VM 設定時執行
#
# 前置條件：
#   - 01-setup-infra.sh 已執行完成
#   - scripts/gcp/vm/.env 已填入正式環境變數（參考 vm/.env.example）
#
# 執行方式：
#   cd scripts/gcp
#   bash 03-setup-vm.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

VM_DIR="${SCRIPT_DIR}/vm"

# 確認 .env 存在
if [ ! -f "${VM_DIR}/.env" ]; then
  warn "找不到 scripts/gcp/vm/.env"
  echo "請先複製範本並填入正式值："
  echo "  cp scripts/gcp/vm/.env.example scripts/gcp/vm/.env"
  exit 1
fi

# =============================================================================
# 1. 設定 Artifact Registry 認證（VM 拉取 Docker Image 用）
# =============================================================================
log "設定 VM 的 Artifact Registry 認證（root）..."
gcloud compute ssh "${VM_NAME}" \
  --zone="${ZONE}" \
  --project="${PROJECT_ID}" \
  --command="sudo gcloud auth configure-docker asia-east1-docker.pkg.dev --quiet"

# =============================================================================
# 2. 建立工作目錄
# =============================================================================
log "建立 VM 工作目錄..."
gcloud compute ssh "${VM_NAME}" \
  --zone="${ZONE}" \
  --project="${PROJECT_ID}" \
  --command="sudo mkdir -p ${VM_WORKDIR} && sudo chown \$USER:docker ${VM_WORKDIR}"

# =============================================================================
# 3. 上傳 Docker Compose 設定與環境變數
# =============================================================================
log "上傳 docker-compose.yml..."
gcloud compute scp \
  "${VM_DIR}/docker-compose.yml" \
  "${VM_NAME}:${VM_WORKDIR}/docker-compose.yml" \
  --zone="${ZONE}" \
  --project="${PROJECT_ID}"

log "上傳 .env..."
gcloud compute scp \
  "${VM_DIR}/.env" \
  "${VM_NAME}:${VM_WORKDIR}/.env" \
  --zone="${ZONE}" \
  --project="${PROJECT_ID}"

# =============================================================================
# 4. 啟動服務
# =============================================================================
log "啟動 VM 上的服務..."
gcloud compute ssh "${VM_NAME}" \
  --zone="${ZONE}" \
  --project="${PROJECT_ID}" \
  --command="cd ${VM_WORKDIR} && \
    sudo docker compose pull && \
    sudo docker compose up -d && \
    sudo docker compose ps"

# =============================================================================
# 完成
# =============================================================================
echo ""
echo -e "${GREEN}===== VM 設定完成 =====${NC}"
echo ""
echo "檢查服務狀態："
echo "  gcloud compute ssh ${VM_NAME} --zone=${ZONE} --command='cd ${VM_WORKDIR} && sudo docker compose ps'"
echo ""
echo "查看 Celery Worker 日誌："
echo "  gcloud compute ssh ${VM_NAME} --zone=${ZONE} --command='cd ${VM_WORKDIR} && sudo docker compose logs -f celery-worker'"