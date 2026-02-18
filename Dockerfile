# Network Configuration Backup System — All-in-One Image
# Single container: Python + Ansible + Node.js + FastAPI + React
# Base: ubuntu:22.04 — no Docker Hub pulls needed at runtime
# -------------------------------------------------------------------------------

FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies + Node.js 20 (via NodeSource)
RUN apt-get update && apt-get install -y \
    software-properties-common \
    python3 \
    python3-pip \
    python3-venv \
    ansible \
    cron \
    vim \
    sshpass \
    libssh-4 \
    iproute2 \
    iputils-ping \
    less \
    bat \
    jq \
    tzdata \
    git \
    curl \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Ansible collections
RUN ansible-galaxy collection install cisco.nxos cisco.ios fortinet.fortios ansible.netcommon

# Install Node.js dependencies (baked into image so npm install isn't needed at runtime)
COPY frontend/package.json frontend/package-lock.json* frontend/
RUN cd frontend && npm install

# Copy project files
COPY . .

# Create output directories
RUN mkdir -p output/configs output/changes output/logs

# Make scripts executable
RUN chmod +x scripts/*.py scripts/*.sh docker-entrypoint.sh

# Set timezone
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

EXPOSE 5173 8000

CMD ["/app/docker-entrypoint.sh"]
