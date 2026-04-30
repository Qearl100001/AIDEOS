# Docker 使用指南

本项目使用 Docker 进行容器化部署。

## 版本说明

版本号存储在 `VERSION` 文件中，当前版本：**1.0.0**

Docker 镜像使用以下版本标签：

| 标签 | 说明 | 示例 |
|-------|------|------|
| `latest` | 最新稳定版 | 从 VERSION 读取 |
| `v{VERSION}` | 语义化版本 | `v1.0.0` |
| `sha-{SHORT_SHA}` | Git commit SHA | `sha-abc1234` |
| `YYYY-MM-DD` | 构建日期 | `2026-04-30` |

## 构建镜像

```bash
# 本地构建镜像（默认 latest）
docker build -t dfos/design:latest .

# 构建带版本标签的镜像（从 VERSION 文件读取）
VERSION=$(cat VERSION)
docker build -t dfos/design:v${VERSION} .

## 运行容器

```bash
# 使用 docker-compose 运行
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 推送镜像

```bash
# 登录阿里云 ACR
docker login crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com -u <RAM用户ID>

# 打标签
docker tag dfos/design:latest crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com/dfos/design:latest

# 推送
docker push crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com/dfos/design:latest
```

## 拉取镜像

```bash
# 登录阿里云 ACR
docker login crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com -u <RAM用户ID>

# 拉取镜像
docker pull crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com/dfos/design:latest

# 登出
docker logout crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com
```

## 部署命令

```bash
# 停止旧容器
docker-compose down

# 启动新容器
docker-compose up -d

# 或使用 docker-compose 重新创建
docker-compose up -d --force-recreate
```

## 查看状态

```bash
# 容器列表
docker ps

# 镜像列表
docker images

# 日志查看
docker logs -f dfos
```

## 常用命令速查

| 操作 | 命令 |
|------|------|
| 构建 | `docker build -t dfos/design:latest .` |
| 构建+版本 | `docker build -t dfos/design:v$(cat VERSION) .` |
| 运行 | `docker-compose up -d` |
| 停止 | `docker-compose down` |
| 查看日志 | `docker-compose logs -f` |
| 进入容器 | `docker exec -it dfos bash` |
| 推送 latest | `docker push crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com/dfos/design:latest` |
| 推送版本 | `docker push crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com/dfos/design:v$(cat VERSION)` |
| 拉取镜像 | `docker pull crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com/dfos/design:latest` |
| 拉取版本 | `docker pull crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com/dfos/design:v1.0.0` |

## 升级版本

修改 `VERSION` 文件后，重新构建并推送：

```bash
# 1. 手动修改版本号
echo "1.0.1" > VERSION

# 2. 构建镜像
docker build -t dfos/design:v1.0.1 .

# 3. 推送镜像
docker tag dfos/design:v1.0.1 crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com/dfos/design:v1.0.1
docker push crpi-y2mlko5kogge3g4i.cn-hongkong.personal.cr.aliyuncs.com/dfos/design:v1.0.1
```

## 自动递增版本

使用脚本自动递增 patch 版本号：

```bash
# 递增 VERSION（需要先安装 yq）
brew install yq

# 或使用 Python 脚本
python3 -c "
import os
v = open('VERSION').read().strip()
v = v.split('.')
v[-1] = str(int(v[-1]) + 1)
open('VERSION', 'w').write('.'.join(v))
"
```

## 环境变量

运行容器时需要配置以下环境变量：

```bash
# 方式一：.env 文件
ANTHROPIC_API_KEY=your_api_key
DOUBAO_API_KEY=your_doubao_key
DOUBAO_RESOURCE_ID=seed-tts-2.0

# 方式二：docker-compose 环境变量
docker-compose -f docker-compose.yml run -e ANTHROPIC_API_KEY=xxx dfos
```