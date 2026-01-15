#!/bin/bash
# Setup Ansible Vault for credential encryption
# Run this script once to encrypt your credentials file

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SECRETS_FILE="$PROJECT_ROOT/playbooks/group_vars/all.yml"
VAULT_PASSWORD_FILE="$PROJECT_ROOT/vault_password.txt"

echo "=== Ansible Vault Setup ==="
echo

# Check if secrets file exists
if [ ! -f "$SECRETS_FILE" ]; then
    echo "Error: Secrets file not found: $SECRETS_FILE"
    exit 1
fi

# Check if already encrypted
if head -1 "$SECRETS_FILE" | grep -q '^\$ANSIBLE_VAULT'; then
    echo "Secrets file is already encrypted."
    echo "To edit: ansible-vault edit $SECRETS_FILE"
    echo "To decrypt: ansible-vault decrypt $SECRETS_FILE"
    exit 0
fi

echo "This script will:"
echo "1. Create a vault password file"
echo "2. Encrypt your credentials in $SECRETS_FILE"
echo

# Create vault password file
if [ ! -f "$VAULT_PASSWORD_FILE" ]; then
    echo "Enter your vault password (will be stored in $VAULT_PASSWORD_FILE):"
    read -s VAULT_PASSWORD
    echo "$VAULT_PASSWORD" > "$VAULT_PASSWORD_FILE"
    chmod 600 "$VAULT_PASSWORD_FILE"
    echo "Vault password file created."
else
    echo "Vault password file already exists."
fi

# Edit the secrets file first
echo
echo "Please edit the secrets file with your actual credentials:"
echo "  $SECRETS_FILE"
echo
read -p "Press Enter when ready to encrypt..."

# Encrypt the file
ansible-vault encrypt "$SECRETS_FILE" --vault-password-file "$VAULT_PASSWORD_FILE"

echo
echo "=== Setup Complete ==="
echo
echo "Your credentials are now encrypted!"
echo
echo "To run playbooks:"
echo "  python scripts/orchestrator.py --vault-password-file vault_password.txt"
echo
echo "To edit credentials:"
echo "  ansible-vault edit playbooks/group_vars/all.yml --vault-password-file vault_password.txt"
echo
echo "IMPORTANT: Add vault_password.txt to .gitignore (already done)"
