FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖（Playwright 浏览器由 python -m playwright install 下载，无需 apt 装 chromium）
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖（含 playwright 包后才有 CLI）
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器及系统库（须在用 pip 安装 playwright 之后）
RUN python -m playwright install --with-deps chromium

# 复制应用代码
COPY . .

# 安装 crond (定时任务)
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# 写 crontab
RUN echo "0 7 * * * bash /app/scripts/full-daily.sh >> /app/logs/\$(date +\%Y-\%m-\%d).log 2>&1" > /etc/cron.d/dfos-cron && \
    chmod 0644 /etc/cron.d/dfos-cron

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["bash", "-c", "crond && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]