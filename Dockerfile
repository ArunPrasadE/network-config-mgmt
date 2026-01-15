# 1. Create Docker Container (Ubuntu 20.04) and install dependencies for Ansible automation
# --------------------------------------------------------------------------------

# Tells Docker to use the official Ubuntu 20.04 image as the base
FROM ubuntu:20.04

# Prevents the system from asking questions during software installations
ENV DEBIAN_FRONTEND=noninteractive

# Installs the required software
RUN apt-get update && apt-get install -y \
    software-properties-common \
    python3 \
    python3-pip \
    python3-venv \
    ansible \
    cron \
    fontconfig-config \
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
    && apt-get clean


# Copy the playbook files to new Docker image (The file should be under the same dir with Dockerfile)
COPY ./playbook-files/inv_mgmt_playbook_v5-added-git-push /inv_mgmt_playbook
COPY ./documentations /documentation

# Default command when the container runs
CMD ["bash"]

RUN pip install --upgrade ansible
RUN pip install paramiko

# Set date and time 
## to JST
# RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
# echo "Asia/Tokyo" > /etc/timezone && \
# RUN dpkg-reconfigure -f noninteractive tzdata

## to IST
# RUN ln -sf /usr/share/zoneinfo/Asia/Kolkata /etc/localtime
# echo "Asia/Kolkata" > /etc/timezone && \
# RUN dpkg-reconfigure -f noninteractive tzdata