#!/bin/bash

if [ "$(id -u)" -ne "0" ]; then
    echo "This script must be run as root. Please use 'sudo ./setup.sh'." >&2
    exit 1
fi

# Update and upgrade the system
apt update && sudo apt upgrade -y

# Install Docker
apt install -y docker.io

# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
dpkg -i minikube_latest_amd64.deb

# Install necessary packages and Kubernetes APT repository key
apt install -y apt-transport-https ca-certificates curl gnupg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# Add Kubernetes APT repository and install kubectl
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
chmod 644 /etc/apt/sources.list.d/kubernetes.list

# Add Helm repository key and install Helm
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list


#Install Kubectl and Helm
apt update
apt install -y helm kubectl


echo "export NAMESPACE=runners" >> .bashrc
echo "export TOKEN=<your-token>" >> .bashrc
source .bashrc

usermod -aG docker ubuntu
newgrp docker

echo "Dependencies are fully installed"

echo "setting up ssh keys"
#!/bin/bash

# Variables
KEY_NAME="github_deploy_key"
KEY_PATH="/home/ubuntu/.ssh/$KEY_NAME"
PUBLIC_KEY_PATH="$KEY_PATH.pub"

# Generate SSH key pair
echo "Generating SSH key pair..."
ssh-keygen -t rsa -b 4096 -f "$KEY_PATH" -N ""

# Append public key to authorized_keys
echo "Adding public key to authorized_keys..."
cat "$PUBLIC_KEY_PATH" >> /home/ubuntu/.ssh/authorized_keys

echo "SSH key setup is complete. Please add the private key to your GitHub repository secrets."
sleep 5
clear
sudo cat /home/ubuntu/.ssh/github_deploy_key
