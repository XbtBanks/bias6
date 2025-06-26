# FinansLab Bias 7/24 Deployment Rehberi

## 1. DigitalOcean VPS Kurulum

### Adım 1: DigitalOcean Hesabı
1. [digitalocean.com](https://digitalocean.com) adresine git
2. Hesap oluştur (kredi kartı gerekli)
3. $100 ücretsiz kredi alabilirsin

### Adım 2: Droplet Oluştur
1. "Create" → "Droplets"
2. **Image**: Ubuntu 22.04 LTS
3. **Plan**: Basic $6/ay (1GB RAM, 1 vCPU)
4. **Region**: Frankfurt (Türkiye'ye yakın)
5. **Authentication**: SSH Key veya Password
6. **Hostname**: finanslab-server
7. "Create Droplet"

### Adım 3: Server'a Bağlan
```bash
# Terminal/CMD ile
ssh root@[server-ip-adresi]
```

## 2. Sunucu Kurulumu

### Python ve Gerekli Paketler
```bash
# Sistem güncelle
apt update && apt upgrade -y

# Python ve pip kur
apt install python3 python3-pip git screen nginx -y

# Pip güncelle
pip3 install --upgrade pip
```

### Proje İndir ve Kur
```bash
# Ana dizine git
cd /root

# Projeyi indir (zip olarak)
wget https://github.com/[kullanici]/finanslab-bias/archive/main.zip
unzip main.zip
cd finanslab-bias-main

# Veya git clone
git clone https://github.com/[kullanici]/finanslab-bias.git
cd finanslab-bias
```

### Python Paketleri Kur
```bash
# Gerekli paketleri kur
pip3 install streamlit yfinance pandas numpy plotly requests

# Veya requirements.txt ile
pip3 install -r app_requirements.txt
```

## 3. Sistem Servis Olarak Çalıştır

### Systemd Servisi Oluştur
```bash
# Servis dosyası oluştur
nano /etc/systemd/system/finanslab.service
```

Dosya içeriği:
```ini
[Unit]
Description=FinansLab Bias Trading System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/finanslab-bias
ExecStart=/usr/bin/python3 -m streamlit run finanslab_unified.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Servisi Başlat
```bash
# Servisi etkinleştir
systemctl daemon-reload
systemctl enable finanslab
systemctl start finanslab

# Durumu kontrol et
systemctl status finanslab
```

## 4. Nginx Reverse Proxy (Opsiyonel)

### Nginx Konfigürasyon
```bash
# Nginx config dosyası
nano /etc/nginx/sites-available/finanslab
```

Dosya içeriği:
```nginx
server {
    listen 80;
    server_name [server-ip-adresi];

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
```

```bash
# Siteyi etkinleştir
ln -s /etc/nginx/sites-available/finanslab /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## 5. Firewall Ayarları

```bash
# UFW firewall kur
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable
```

## 6. Erişim

### Doğrudan Streamlit
- http://[server-ip]:8501

### Nginx üzerinden
- http://[server-ip]

## 7. Yönetim Komutları

```bash
# Servisi durdur
systemctl stop finanslab

# Servisi başlat
systemctl start finanslab

# Servisi yeniden başlat
systemctl restart finanslab

# Log görüntüle
journalctl -u finanslab -f

# Sistem durumu
systemctl status finanslab
```

## 8. Güncelleme

```bash
# Kodu güncelle
cd /root/finanslab-bias
git pull origin main

# Servisi yeniden başlat
systemctl restart finanslab
```

## 9. Monitoring

```bash
# CPU/RAM kullanımı
htop

# Disk kullanımı
df -h

# Streamlit logları
tail -f ~/.streamlit/logs/streamlit.log
```

## 10. Backup

```bash
# Haftalık backup scripti
#!/bin/bash
tar -czf /root/backup-$(date +%Y%m%d).tar.gz /root/finanslab-bias
```

## Maliyet
- **DigitalOcean**: $6/ay (1GB RAM)
- **Domain** (opsiyonel): $10-15/yıl
- **SSL** (Let's Encrypt): Ücretsiz

## Sorun Giderme

### Servis Çalışmıyor
```bash
systemctl status finanslab
journalctl -u finanslab --no-pager
```

### Port Problemi
```bash
netstat -tlnp | grep 8501
```

### Python Paket Hatası
```bash
pip3 install --upgrade [paket-adi]
```

Bu rehberle sistemin 7/24 çalışacak hale gelir.