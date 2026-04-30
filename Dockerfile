FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libffi-dev \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# 安装 Playwright 浏览器
RUN playwright install --with-deps chromium

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

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