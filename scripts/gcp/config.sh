#!/bin/bash
# =============================================================================
# GCP 部署共用設定
# 所有腳本透過 source ./config.sh 載入此設定
# =============================================================================

# --- 專案基本設定 ---
export PROJECT_ID="cy-ecommerce-v1"
export REGION="asia-east1"
export ZONE="asia-east1-b"

# --- Cloud Run ---
export CLOUD_RUN_SERVICE="cy-ecommerce-api"

# --- Cloud SQL ---
export CLOUD_SQL_INSTANCE="cy-ecommerce-db"
export CLOUD_SQL_DB="ecommerce"
export CLOUD_SQL_USER="ecommerce_user"
# Cloud SQL 連線名稱格式: PROJECT_ID:REGION:INSTANCE_NAME
export CLOUD_SQL_CONNECTION_NAME="${PROJECT_ID}:${REGION}:${CLOUD_SQL_INSTANCE}"

# --- GCE VM (Redis + Celery Worker) ---
export VM_NAME="cy-ecommerce-worker"
export VM_MACHINE_TYPE="e2-small"
export VM_TAG="redis-server"

# --- Artifact Registry ---
export ARTIFACT_REPO="cy-ecommerce-repo"
export IMAGE_NAME="cy-ecommerce-api"
export IMAGE_FULL="asia-east1-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/${IMAGE_NAME}"

# --- VPC Connector ---
export VPC_CONNECTOR="cy-ecommerce-connector"
export VPC_CONNECTOR_RANGE="10.8.0.0/28"

# --- Service Accounts ---
export SA_CLOUD_RUN="cy-ecommerce-api-sa"
export SA_VM="cy-ecommerce-worker-sa"
export SA_SCHEDULER="cy-ecommerce-scheduler-sa"
export SA_CD="cy-ecommerce-cd-sa"

# --- Workload Identity Federation (GitHub Actions CD) ---
export WIF_POOL="github-actions-pool"
export WIF_PROVIDER="github-actions-provider"
export GITHUB_REPO="JeterChan/cy-ecommerce-web"

# --- Cloud Scheduler ---
export SCHEDULER_JOB="hard-delete-expired-accounts"

# --- VM 上的工作目錄 ---
export VM_WORKDIR="/opt/cy-ecommerce"
