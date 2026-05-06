#!/bin/bash
apt update
apt install -y python3-pip python3-venv postgresql nginx git ufw
pip3 install gunicorn

# Config PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE amenagement_db;"
sudo -u postgres psql -c "CREATE USER django_user WITH PASSWORD 'password123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE amenagement_db TO django_user;"

# Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# Firewall
ufw allow 22
ufw allow 80
ufw --force enable

echo "Prêt ! Clone ton repo avec: git clone https://github.com/TON_USERNAME/amenagement.git /var/www/amenagement"