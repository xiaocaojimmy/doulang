FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY setup.py .
COPY README.md .
COPY src/ ./src/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装豆语
RUN pip install -e .

# 创建数据目录
RUN mkdir -p /app/data /app/memory

# 暴露端口
EXPOSE 8080

# 默认命令
CMD ["python", "-m", "doulang.server"]
