#!/bin/bash

set -e

echo "========================================"
echo " 🚀 Server Initial Setup Started"
echo "========================================"

### Colors
GREEN="\e[32m"
RED="\e[31m"
BLUE="\e[34m"
RESET="\e[0m"

### Check root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo ./setup.sh)${RESET}"
  exit 1
fi

echo -e "${BLUE}🔹 Step 1: Adding Swap Memory (2GB)${RESET}"

if swapon --show | grep -q "/swapfile"; then
  echo -e "${GREEN}✔ Swap already exists, skipping${RESET}"
else
  fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  echo -e "${GREEN}✔ Swap added successfully${RESET}"
fi

echo -e "${BLUE}🔹 Setting swappiness for Docker${RESET}"
sysctl vm.swappiness=10
echo 'vm.swappiness=10' > /etc/sysctl.d/99-docker.conf
sysctl -p /etc/sysctl.d/99-docker.conf

echo -e "${BLUE}🔹 Step 2: System Update${RESET}"
apt update && apt upgrade -y

echo -e "${BLUE}🔹 Step 3: Installing Git${RESET}"
apt install -y git

echo -e "${BLUE}🔹 Step 4: Installing Docker & Docker Compose (Latest)${RESET}"

apt install -y ca-certificates curl gnupg lsb-release
mkdir -p /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/debian \
$(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo -e "${BLUE}🔹 Step 5: Enable & Start Docker Services${RESET}"
systemctl enable docker
systemctl start docker

systemctl enable containerd
systemctl start containerd

echo -e "${BLUE}🔹 Step 6: Docker Non-root Access${RESET}"
usermod -aG docker ${SUDO_USER:-$USER}

echo -e "${GREEN}✔ Docker user permission applied (re-login required)${RESET}"

echo "========================================"
echo " ✅ Installation Successful"
echo "========================================"

echo -e "${BLUE}📦 Versions:${RESET}"
git --version
docker --version
docker compose version

echo
echo -e "${BLUE}💾 Memory Status:${RESET}"
free -h

echo
echo -e "${GREEN}🎉 Setup Completed Successfully${RESET}"
echo "➡ Please logout/login or reboot to use docker without sudo"
echo "========================================"
