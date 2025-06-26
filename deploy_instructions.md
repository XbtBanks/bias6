# FinansLab 7/24 Deployment - Basit Rehber

## Hızlı Kurulum (5 Dakika)

### 1. VPS Satın Al
- **DigitalOcean** veya **Contabo** öneriyorum
- En ucuz plan yeterli ($4-6/ay)
- Ubuntu 22.04 seç

### 2. Server'a Bağlan
```bash
ssh root@[ip-adresi]
```

### 3. Otomatik Kurulum
```bash
# Kurulum scriptini indir ve çalıştır
wget https://raw.githubusercontent.com/[repo]/setup.sh
chmod +x setup.sh
./setup.sh
```

### 4. Ana Dosyayı Kopyala
```bash
# Bu projedeki finanslab_unified.py dosyasını server'a yükle
nano /opt/finanslab/finanslab_unified.py
# Dosya içeriğini yapıştır ve kaydet (Ctrl+X, Y, Enter)
```

### 5. Başlat
```bash
systemctl start finanslab
systemctl status finanslab
```

## Erişim
- http://[server-ip] adresinden sisteme erişebilirsin
- 7/24 çalışacak, kapanmayacak

## Yönetim
```bash
# Durumu kontrol et
systemctl status finanslab

# Yeniden başlat
systemctl restart finanslab

# Logları gör
journalctl -u finanslab -f
```

## Platform Önerileri

### En Ucuz: Contabo
- $4.99/ay
- 4GB RAM, 2 CPU
- Almanya lokasyon

### En Kolay: DigitalOcean  
- $6/ay
- 1GB RAM, 1 CPU
- Türkiye'ye yakın

### Ücretsiz Deneme: AWS
- 12 ay ücretsiz
- t2.micro instance
- Karmaşık kurulum

## Dosyalar
Bu projedeki şu dosyaları server'a kopyalaman gerekiyor:
- `finanslab_unified.py` (ana sistem)
- `setup.sh` (kurulum scripti)

Kurulum sonrası sistem otomatik başlayacak ve kesintisiz çalışacak.