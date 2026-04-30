#!/bin/bash
#
# 服务器部署脚本
# 用途：SSH 登录服务器后执行，用于拉取最新镜像并重启服务
#
# 使用方式：
#   bash deploy-server.sh [tag]
#   tag 默认值为 latest
#
# 环境变量（在 .env 中配置或作为参数传入）：
#   REGISTRY - 镜像仓库地址
#   IMAGE_NAME - 镜像名称
#   DOCKER_REGISTRY_USER - 用户名
#   DOCKER_REGISTRY_PASSWORD - 密码
#   （脚本会根据 tag 自动 export DFOS_IMAGE_TAG，供 docker-compose.yml 中 image 插值）
#   DEPLOY_TAG - 可选，指定镜像 tag（CI 注入，覆盖第一个参数）
#   DEPLOY_DIR - 可选，compose 与 .env 所在目录（CI script_path 时设 /DEOS）
#

set -e

# 配置
REGISTRY="${REGISTRY:-crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com}"
IMAGE_NAME="${IMAGE_NAME:-dfos/design}"
# 镜像标签：优先环境变量 DEPLOY_TAG（CI script_path），否则取第一个参数
TAG="${DEPLOY_TAG:-${1:-latest}}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

# 工作目录：优先 DEPLOY_DIR（CI 传入 /DEOS，因 script_path 在远端临时路径执行）；
# 否则为脚本所在目录（本机/服务器手动：在目录下 bash deploy-server.sh）
if [[ -n "${DEPLOY_DIR:-}" ]]; then
  cd "${DEPLOY_DIR}" || { echo "[deploy-server] cannot cd to ${DEPLOY_DIR}" >&2; exit 1; }
else
  _here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "${_here}" || exit 1
fi

FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${TAG}"

# Compose V2: docker compose；旧版：docker-compose
compose() {
  if docker compose version >/dev/null 2>&1; then
    docker compose -f "${COMPOSE_FILE}" "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose -f "${COMPOSE_FILE}" "$@"
  else
    echo "[deploy-server] 未找到 docker compose / docker-compose，请安装 Docker Compose。" >&2
    exit 127
  fi
}

echo "=== Deploying ${FULL_IMAGE} ==="

# 登录 ACR
echo "${DOCKER_REGISTRY_PASSWORD}" | docker login ${REGISTRY} -u "${DOCKER_REGISTRY_USER}" --password-stdin

# 拉取最新镜像
docker pull ${FULL_IMAGE}

# 与 docker-compose.yml 中 image:${DFOS_IMAGE_TAG} 对齐
export DFOS_IMAGE_TAG="${TAG}"

# 停止旧容器
compose down || true

# 启动新容器
compose up -d

# 退出登录（安全）
docker logout ${REGISTRY} || true

echo "=== Deployed ${FULL_IMAGE} ==="