#!/bin/bash
# =============================================================================
# 01-setup-infra.sh — GCP 基礎設施一次性建立腳本
#
# 用途：建立所有 GCP 資源，可安全重複執行（已存在的資源會跳過）
# 執行頻率：首次部署時執行一次，或新增資源時執行
#
# 執行方式：
#   cd scripts/gcp
#   bash 01-setup-infra.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

# 確認 vm/.env 存在並載入（Secret Manager 需要從中讀取正式值）
VM_ENV_FILE="${SCRIPT_DIR}/vm/.env"
if [ ! -f "${VM_ENV_FILE}" ]; then
  echo "ERROR: 找不到 scripts/gcp/vm/.env，請先建立並填入正式值："
  echo "  cp scripts/gcp/vm/.env.example scripts/gcp/vm/.env"
  exit 1
fi
source "${VM_ENV_FILE}"

# 顏色輸出
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

log "啟用所需 API（已啟用的會自動跳過）..."
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  cloudscheduler.googleapis.com \
  vpcaccess.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com

# =============================================================================
# 1. Artifact Registry — 儲存 Docker Image
#
# 設計原因：
#   Cloud Run 部署時需要從 Image Registry 拉取映像檔。
#   Artifact Registry 和 GCP 同一個專案，透過 IAM 自動認證，
#   不需要額外的 Registry 帳密設定。
# =============================================================================
log "建立 Artifact Registry..."
if ! gcloud artifacts repositories describe "${ARTIFACT_REPO}" \
    --location="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud artifacts repositories create "${ARTIFACT_REPO}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="CY Ecommerce Docker images"
  log "Artifact Registry 建立完成。"
else
  skip "Artifact Registry ${ARTIFACT_REPO}"
fi

# =============================================================================
# 2. Service Accounts — 最小權限原則
#
# 設計原因：
#   各服務使用獨立的 Service Account，只授予必要的 IAM 角色，
#   避免單一帳號洩漏造成全部資源受影響。
#   - Cloud Run SA：存取 Cloud SQL、讀取 Secrets
#   - VM SA：存取 Cloud SQL（Auth Proxy）、拉取 Docker Image
#   - Scheduler SA：呼叫 Cloud Run 的權限
# =============================================================================
log "建立 Service Accounts..."

for SA_NAME in "${SA_CLOUD_RUN}" "${SA_VM}" "${SA_SCHEDULER}"; do
  if ! gcloud iam service-accounts describe \
      "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --project="${PROJECT_ID}" &>/dev/null; then
    gcloud iam service-accounts create "${SA_NAME}" \
      --display-name="${SA_NAME}" \
      --project="${PROJECT_ID}"
    log "Service Account ${SA_NAME} 建立完成。"
  else
    skip "Service Account ${SA_NAME}"
  fi
done

# Cloud Run SA 權限
log "設定 Cloud Run Service Account 權限..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_CLOUD_RUN}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client" --condition=None

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_CLOUD_RUN}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" --condition=None

# VM SA 權限：Cloud SQL 連線 + 拉取 Docker Image
log "設定 VM Service Account 權限..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_VM}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client" --condition=None

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_VM}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.reader" --condition=None

# Scheduler SA 權限：只能呼叫 Cloud Run（部署後再設定）
log "設定 Scheduler Service Account 權限..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_SCHEDULER}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.invoker" --condition=None

# =============================================================================
# 3. Cloud SQL — 託管 PostgreSQL
#
# 設計原因：
#   Cloud SQL 提供自動備份、高可用性、維護視窗管理。
#   使用 db-f1-micro 控制成本（~$8/月）。
#   不開 Private IP，改用 Cloud SQL Auth Proxy 連線，
#   不需要複雜的 VPC Peering 設定，且 IAM 認證更安全。
# =============================================================================
log "建立 Cloud SQL 執行個體（可能需要 5-10 分鐘）..."
if ! gcloud sql instances describe "${CLOUD_SQL_INSTANCE}" \
    --project="${PROJECT_ID}" &>/dev/null; then
  gcloud sql instances create "${CLOUD_SQL_INSTANCE}" \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region="${REGION}" \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --availability-type=zonal \
    --database-flags=max_connections=50 \
    --project="${PROJECT_ID}"
  log "Cloud SQL 建立完成。"
else
  skip "Cloud SQL ${CLOUD_SQL_INSTANCE}"
fi

log "建立資料庫..."
if ! gcloud sql databases describe "${CLOUD_SQL_DB}" \
    --instance="${CLOUD_SQL_INSTANCE}" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud sql databases create "${CLOUD_SQL_DB}" \
    --instance="${CLOUD_SQL_INSTANCE}" \
    --project="${PROJECT_ID}"
  log "資料庫 ${CLOUD_SQL_DB} 建立完成。"
else
  skip "資料庫 ${CLOUD_SQL_DB}"
fi

log "建立資料庫使用者..."
# 注意：gcloud sql users list 無法直接判斷使用者是否存在，強制建立若衝突則忽略
gcloud sql users create "${CLOUD_SQL_USER}" \
  --instance="${CLOUD_SQL_INSTANCE}" \
  --password="${DB_PASSWORD}" \
  --project="${PROJECT_ID}" 2>/dev/null || {
    # 使用者已存在，更新密碼
    gcloud sql users set-password "${CLOUD_SQL_USER}" \
      --instance="${CLOUD_SQL_INSTANCE}" \
      --password="${DB_PASSWORD}" \
      --project="${PROJECT_ID}"
    log "資料庫使用者密碼已更新。"
  }

# =============================================================================
# 4. Secret Manager — 機密資料管理
#
# 設計原因：
#   敏感資訊（密碼、API Key）不應放在環境變數明文中。
#   Secret Manager 提供版本管理、稽核日誌、細粒度 IAM 存取控制。
#   Cloud Run 可直接掛載 Secret 為環境變數，無需程式碼修改。
# =============================================================================
log "建立 Secrets（從 vm/.env 讀取正式值）..."

# 若 Secret 已存在則新增版本（更新值），若不存在則建立
upsert_secret() {
  local SECRET_NAME=$1
  local SECRET_VALUE=$2
  if [ -z "${SECRET_VALUE}" ]; then
    echo "ERROR: vm/.env 中 ${SECRET_NAME} 對應的值為空，請填入後重新執行。" >&2
    exit 1
  fi
  if ! gcloud secrets describe "${SECRET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
    echo -n "${SECRET_VALUE}" | gcloud secrets create "${SECRET_NAME}" \
      --data-file=- --project="${PROJECT_ID}"
    log "Secret ${SECRET_NAME} 建立完成。"
  else
    echo -n "${SECRET_VALUE}" | gcloud secrets versions add "${SECRET_NAME}" \
      --data-file=- --project="${PROJECT_ID}"
    log "Secret ${SECRET_NAME} 已更新為最新版本。"
  fi
}

upsert_secret "db-password"          "${DB_PASSWORD}"
upsert_secret "jwt-secret-key"       "${SECRET_KEY}"
upsert_secret "brevo-api-key"        "${BREVO_API_KEY}"
upsert_secret "aws-access-key-id"    "${AWS_ACCESS_KEY_ID}"
upsert_secret "aws-secret-access-key" "${AWS_SECRET_ACCESS_KEY}"
upsert_secret "cleanup-api-key"      "${CLEANUP_API_KEY}"

# =============================================================================
# 5. VPC Connector — Cloud Run 存取 VPC 內部資源
#
# 設計原因：
#   Cloud Run 預設運行在 Google 管理的網路，無法直接連線 GCE VM 的私有 IP。
#   VPC Connector 建立一座橋，讓 Cloud Run 流量能進入使用者的 VPC，
#   進而存取 GCE VM 上的 Redis（私有 IP）。
#   使用 e2-micro 機型控制成本（~$7/月）。
# =============================================================================
log "建立 VPC Connector..."
if ! gcloud compute networks vpc-access connectors describe "${VPC_CONNECTOR}" \
    --region="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud compute networks vpc-access connectors create "${VPC_CONNECTOR}" \
    --region="${REGION}" \
    --network=default \
    --range="${VPC_CONNECTOR_RANGE}" \
    --min-instances=2 \
    --max-instances=3 \
    --machine-type=e2-micro \
    --project="${PROJECT_ID}"
  log "VPC Connector 建立完成。"
else
  skip "VPC Connector ${VPC_CONNECTOR}"
fi

# =============================================================================
# 6. 防火牆規則 — 限制 Redis 存取來源
#
# 設計原因：
#   GCE VM 上的 Redis port 6379 只允許來自 VPC Connector IP 範圍的流量。
#   Cloud Run 透過 VPC Connector 存取 Redis，其流量來源 IP 在此範圍內。
#   防止外部或其他 VPC 資源直接存取 Redis。
# =============================================================================
log "建立防火牆規則..."
if ! gcloud compute firewall-rules describe "allow-vpc-connector-to-redis" \
    --project="${PROJECT_ID}" &>/dev/null; then
  gcloud compute firewall-rules create "allow-vpc-connector-to-redis" \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:6379 \
    --source-ranges="${VPC_CONNECTOR_RANGE}" \
    --target-tags="${VM_TAG}" \
    --project="${PROJECT_ID}"
  log "防火牆規則建立完成。"
else
  skip "防火牆規則 allow-vpc-connector-to-redis"
fi

# =============================================================================
# 7. GCE VM — Redis + Celery Worker
#
# 設計原因：
#   Redis 需要持久連線和記憶體狀態（購物車、Token、庫存），
#   不適合 Cloud Run 的無狀態/短暫生命週期模型。
#   Celery Worker 是長時間執行的進程，也不適合 Cloud Run。
#   將兩者共置同一 VM：Redis 作為 broker，Worker 用 localhost 連線，
#   最低延遲、最省成本（e2-small ~$6/月）。
#
#   VM 上另外跑 Cloud SQL Auth Proxy，讓 Celery Worker 的購物車同步任務
#   能安全連線至 Cloud SQL（透過 IAM 認證，不需要明文密碼傳輸）。
# =============================================================================
log "建立 GCE VM..."
if ! gcloud compute instances describe "${VM_NAME}" \
    --zone="${ZONE}" --project="${PROJECT_ID}" &>/dev/null; then

  # startup-script：VM 首次啟動時自動安裝 Docker
  gcloud compute instances create "${VM_NAME}" \
    --zone="${ZONE}" \
    --machine-type="${VM_MACHINE_TYPE}" \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --tags="${VM_TAG}" \
    --service-account="${SA_VM}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --scopes=cloud-platform \
    --project="${PROJECT_ID}" \
    --metadata=startup-script='#!/bin/bash
# Docker 安裝
apt-get update
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable docker
systemctl start docker
# 建立工作目錄
mkdir -p /opt/cy-ecommerce'

  log "GCE VM 建立完成。等待 VM 啟動完成（約 60 秒）..."
  sleep 60
else
  skip "GCE VM ${VM_NAME}"
fi

# 取得 VM 的內部 IP
VM_INTERNAL_IP=$(gcloud compute instances describe "${VM_NAME}" \
  --zone="${ZONE}" \
  --format="value(networkInterfaces[0].networkIP)" \
  --project="${PROJECT_ID}")

log "VM 內部 IP：${VM_INTERNAL_IP}"
echo ""
echo -e "${YELLOW}請記下此 IP，部署 Cloud Run 時設定 REDIS_URL 需要用到：${NC}"
echo "   REDIS_URL=redis://${VM_INTERNAL_IP}:6379/0"
echo ""

# =============================================================================
# 完成
# =============================================================================
echo ""
echo -e "${GREEN}===== 基礎設施設定完成 =====${NC}"
echo ""
echo "後續步驟："
echo "  1. 更新 Secrets 為正式值（見上方提示）"
echo "  2. 執行 02-deploy.sh 部署應用程式"
echo "  3. 將 VM docker-compose.yml 和 .env 複製到 VM 上"
echo "     bash scripts/gcp/03-setup-vm.sh"