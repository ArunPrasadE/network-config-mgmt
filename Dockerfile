# Network Configuration Backup System
# Docker container with Ansible and Python for multi-vendor network automation
# -------------------------------------------------------------------------------

FROM ubuntu:22.04

# Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Ansible collections
RUN ansible-galaxy collection install cisco.nxos cisco.ios fortinet.fortios ansible.netcommon

# Copy project files
COPY ansible.cfg .
COPY playbooks/ ./playbooks/
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# Create output directories
RUN mkdir -p output/configs output/changes output/logs

# Make scripts executable
RUN chmod +x scripts/*.py scripts/*.sh

# Set timezone (uncomment your timezone)
# JST (Japan)
# RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && echo "Asia/Tokyo" > /etc/timezone
# IST (India)
# RUN ln -sf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && echo "Asia/Kolkata" > /etc/timezone
# UTC (default)
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

# Default command
CMD ["bash"]
