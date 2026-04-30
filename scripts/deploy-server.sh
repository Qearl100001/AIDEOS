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
#

set -e

# 配置
REGISTRY="${REGISTRY:-crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com}"
IMAGE_NAME="${IMAGE_NAME:-dfos/design}"
TAG="${1:-latest}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${TAG}"

echo "=== Deploying ${FULL_IMAGE} ==="

# 登录 ACR
echo "${DOCKER_REGISTRY_PASSWORD}" | docker login ${REGISTRY} -u "${DOCKER_REGISTRY_USER}" --password-stdin

# 拉取最新镜像
docker pull ${FULL_IMAGE}

# 停止旧容器
docker-compose -f ${COMPOSE_FILE} down || true

# 启动新容器
docker-compose -f ${COMPOSE_FILE} up -d

# 退出登录（安全）
docker logout ${REGISTRY} || true

echo "=== Deployed ${FULL_IMAGE} ==="