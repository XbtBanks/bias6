#!/bin/bash
# FinansLab Bias Otomatik Kurulum Scripti

echo "FinansLab Bias Kurulumu Başlıyor..."

# Sistem güncelleme
echo "Sistem güncelleniyor..."
apt update && apt upgrade -y

# Gerekli paketler
echo "Python ve gerekli araçlar kuruluyor..."
apt install python3 python3-pip git screen nginx htop -y

# Python paketleri
echo "Python bağımlılıkları kuruluyor..."
pip3 install --upgrade pip
pip3 install streamlit==1.29.0 yfinance==0.2.18 pandas==2.1.4 numpy==1.24.3 plotly==5.17.0 requests==2.31.0

# Proje klasörü
echo "Proje klasörü hazırlanıyor..."
mkdir -p /opt/finanslab
cd /opt/finanslab

# Ana dosyayı kopyala (manual olarak yapılacak)
echo "finanslab_unified.py dosyasını /opt/finanslab/ klasörüne kopyalayın"

# Systemd servis dosyası
echo "Sistem servisi oluşturuluyor..."
cat > /etc/systemd/system/finanslab.service << 'EOF'
[Unit]
Description=FinansLab Bias Trading System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/finanslab
ExecStart=/usr/bin/python3 -m streamlit run finanslab_unified.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Nginx konfigürasyon
echo "Nginx konfigürasyonu oluşturuluyor..."
cat > /etc/nginx/sites-available/finanslab << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Nginx'i etkinleştir
ln -sf /etc/nginx/sites-available/finanslab /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Firewall
echo "Firewall ayarları yapılandırılıyor..."
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Servisleri etkinleştir
echo "Servisler etkinleştiriliyor..."
systemctl daemon-reload
systemctl enable finanslab
systemctl enable nginx

echo "Kurulum tamamlandı!"
echo "Şimdi finanslab_unified.py dosyasını /opt/finanslab/ klasörüne kopyalayın"
echo "Ardından 'systemctl start finanslab' komutuyla başlatın"
echo "Sistem http://server-ip adresinden erişilebilir olacak"