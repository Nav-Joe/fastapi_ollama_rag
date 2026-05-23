FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装supervisor
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

COPY services.py .
COPY app.py .
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 暴露两个端口
EXPOSE 8000 7861

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
