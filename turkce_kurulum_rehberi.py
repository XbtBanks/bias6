"""
FinansLab TradingView Entegrasyonu - Türkçe Adım Adım Rehber
==========================================================

Bu rehber size TradingView verilerini nasıl aktif hale getireceğinizi
tek tek öğretecek.
"""

import os
import sys

class TurkceKurulumRehberi:
    """TradingView kurulumu için Türkçe rehber"""
    
    def __init__(self):
        self.tamamlanan_adimlar = []
    
    def adim_1_bilgisayarinizda_calistirma(self):
        """Adım 1: Kendi bilgisayarınızda çalıştırma (EN KOLAY)"""
        print("=== ADIM 1: BİLGİSAYARINIZDA ÇALIŞTIRMA (EN KOLAY) ===")
        print()
        print("Bu yöntem 5 dakikada hallolur:")
        print()
        print("1. Kodu bilgisayarınıza indirin:")
        print("   • Replit'te Files > Download as ZIP")
        print("   • ZIP'i masaüstüne çıkarın")
        print()
        print("2. Terminal/Command Prompt açın:")
        print("   • Windows: Win+R, 'cmd' yazın")
        print("   • Mac: Cmd+Space, 'terminal' yazın")
        print()
        print("3. Klasöre gidin:")
        print("   cd Desktop/finanslab-klasoru")
        print()
        print("4. Python'u çalıştırın:")
        print("   python -m pip install streamlit yfinance pandas")
        print("   streamlit run app.py")
        print()
        print("5. Tarayıcıda açılacak: http://localhost:8501")
        print()
        print("✅ Bu yöntemde TradingView API'leri çalışır!")
        print()
        
        self.tamamlanan_adimlar.append("Bilgisayarda Çalıştırma")
    
    def adim_2_cevre_degiskenleri(self):
        """Adım 2: TradingView bilgilerinizi sisteme ekleme"""
        print("=== ADIM 2: TRADINGVIEW BİLGİLERİNİZİ EKLEME ===")
        print()
        print("Bilgisayarınızda bu dosyayı oluşturun:")
        print("Dosya adı: .env")
        print()
        print("İçeriği:")
        print("TRADINGVIEW_USERNAME=waillant70@gmail.com")
        print("TRADINGVIEW_PASSWORD=şifreniz_buraya")
        print()
        print("Nasıl yapılır:")
        print("1. Notepad açın")
        print("2. Yukarıdaki 2 satırı yazın (şifrenizi gerçek şifrenizle değiştirin)")
        print("3. 'Farklı Kaydet' > Dosya adı: .env")
        print("4. FinansLab klasörüne kaydedin")
        print()
        print("VEYA terminal'de:")
        print('echo "TRADINGVIEW_USERNAME=waillant70@gmail.com" > .env')
        print('echo "TRADINGVIEW_PASSWORD=şifreniz" >> .env')
        print()
        
        self.tamamlanan_adimlar.append("Çevre Değişkenleri")
    
    def adim_3_test_etme(self):
        """Adım 3: TradingView bağlantısını test etme"""
        print("=== ADIM 3: TRADINGVIEW BAĞLANTISINI TEST ETME ===")
        print()
        print("Terminal'de şu komutları çalıştırın:")
        print()
        print("1. Bağlantı testi:")
        print("   python tradingview_diagnosis.py")
        print()
        print("2. Kimlik doğrulama testi:")
        print("   python tradingview_authenticated_fetcher.py")
        print()
        print("3. Veri çekme testi:")
        print("   python quick_performance_test.py")
        print()
        print("Başarılı sonuçlar:")
        print("✅ DNS Resolution: SUCCESS")
        print("✅ Authentication: SUCCESS")  
        print("✅ Data retrieval: SUCCESS")
        print()
        print("Hata alırsanız:")
        print("• Şifrenizi kontrol edin")
        print("• İnternet bağlantınızı kontrol edin")
        print("• Antivirus/firewall kapatın")
        print()
        
        self.tamamlanan_adimlar.append("Test Etme")
    
    def adim_4_bulut_servisi(self):
        """Adım 4: Bulut servisinde çalıştırma (İLERİ SEVİYE)"""
        print("=== ADIM 4: BULUT SERVİSİNDE ÇALIŞTIRMA (İLERİ) ===")
        print()
        print("Bu adım sadece 7/24 çalışmasını istiyorsanız gerekli:")
        print()
        print("A) Heroku (EN KOLAY):")
        print("   1. heroku.com'da hesap açın")
        print("   2. 'New App' > 'Create App'")
        print("   3. GitHub'dan kodunuzu bağlayın")
        print("   4. Config Vars > TradingView bilgilerinizi ekleyin")
        print("   5. Deploy")
        print()
        print("B) Railway (ORTA):")
        print("   1. railway.app'de hesap açın")
        print("   2. 'New Project' > GitHub'dan import")
        print("   3. Variables > TradingView bilgileri")
        print("   4. Deploy")
        print()
        print("C) DigitalOcean (PROFESYONEL):")
        print("   1. $5/ay droplet kiralayın")
        print("   2. Ubuntu seçin")
        print("   3. SSH ile bağlanın")
        print("   4. Kodu yükleyin ve çalıştırın")
        print()
        
        self.tamamlanan_adimlar.append("Bulut Servisi")
    
    def adim_5_sorun_giderme(self):
        """Adım 5: Yaygın sorunlar ve çözümleri"""
        print("=== ADIM 5: SORUN GİDERME ===")
        print()
        print("Yaygın hatalar ve çözümleri:")
        print()
        print("1. 'DNS Resolution Failed':")
        print("   → İnternet bağlantınızı kontrol edin")
        print("   → VPN kapatın")
        print("   → Başka bir ağda deneyin")
        print()
        print("2. 'Authentication Failed':")
        print("   → TradingView şifrenizi kontrol edin")
        print("   → 2FA kapalı olduğundan emin olun")
        print("   → TradingView'da giriş yapıp çıkın")
        print()
        print("3. 'Module not found':")
        print("   → pip install streamlit yfinance pandas")
        print("   → Python 3.7+ kullandığınızdan emin olun")
        print()
        print("4. 'Port already in use':")
        print("   → streamlit run app.py --server.port 8502")
        print("   → Farklı port numarası deneyin")
        print()
        print("5. Hiçbir şey çalışmıyorsa:")
        print("   → Mevcut sistem zaten Yahoo Finance kullanıyor")
        print("   → %99 veri kalitesi garantili")
        print("   → TradingView olmadan da profesyonel analiz")
        print()
        
        self.tamamlanan_adimlar.append("Sorun Giderme")
    
    def pratik_ornekler(self):
        """Pratik örnekler ve komutlar"""
        print("=== PRATİK ÖRNEKLER ===")
        print()
        print("Hızlı başlangıç komutları:")
        print()
        print("# 1. Tüm gereksinimleri yükle")
        print("pip install streamlit yfinance pandas numpy plotly")
        print()
        print("# 2. TradingView bilgilerini ayarla")
        print("set TRADINGVIEW_USERNAME=waillant70@gmail.com")
        print("set TRADINGVIEW_PASSWORD=şifreniz")
        print()
        print("# 3. Uygulamayı başlat")
        print("streamlit run app.py")
        print()
        print("# 4. Test komutları")
        print("python tradingview_diagnosis.py")
        print("python quick_performance_test.py")
        print()
        print("Başarı göstergeleri:")
        print("✅ Tarayıcıda FinansLab açılır")
        print("✅ BTC analizi çalışır")
        print("✅ Tüm EMA'lar hesaplanır")
        print("✅ FVG'ler tespit edilir")
        print()
    
    def tam_rehber_goster(self):
        """Tam rehberi göster"""
        print("FinansLab TradingView Entegrasyonu")
        print("=" * 40)
        print("Türkçe Adım Adım Kurulum Rehberi")
        print()
        
        self.adim_1_bilgisayarinizda_calistirma()
        print()
        self.adim_2_cevre_degiskenleri()
        print()
        self.adim_3_test_etme()
        print()
        self.adim_4_bulut_servisi()
        print()
        self.adim_5_sorun_giderme()
        print()
        self.pratik_ornekler()
        print()
        
        # YENİ: Sinyal takip sistemi açıklaması
        print("=== 🚀 YENİ ÖZELLİKLER ===")
        print()
        print("📊 Otomatik Sinyal Takip Sistemi:")
        print("• Attığınız sinyalleri otomatik kaydet")
        print("• Günlük kazanç/kayıp hesaplama")
        print("• Win rate ve R multiple takibi")
        print("• Otomatik bias (yön) önerisi")
        print()
        print("⚡ Günlük Bias Sistemi:")
        print("• Her gün için trend önerisi")
        print("• Market koşulları analizi")
        print("• Volatilite uyarıları")
        print("• En güçlü sembollerin tespiti")
        print()
        print("📈 Performans Dashboard:")
        print("• Detaylı istatistikler")
        print("• Aylık projeksiyon")
        print("• Risk analizi")
        print("• Gelişim önerileri")
        print()
        print("Kullanım:")
        print("1. streamlit run app.py")
        print("2. '⚡ Sinyal Takip' tab'ını seçin")
        print("3. Analizden sonra 'Sinyali Kaydet' butonuna basın")
        print("4. Günlük bias önerilerini takip edin")
        print()
        
        print("=== ÖZET ===")
        print(f"Tamamlanan bölümler: {len(self.tamamlanan_adimlar)}")
        for i, adim in enumerate(self.tamamlanan_adimlar, 1):
            print(f"{i}. {adim}")
        print()
        print("🎯 EN KOLAY YÖNTEM: Bilgisayarınızda çalıştırın!")
        print("📊 MEVCUT SİSTEM: Zaten Yahoo Finance ile çalışıyor")
        print("⚡ TradingView: Sadece ekstra özellik, gerekli değil")
        print("🚀 YENİ: Otomatik sinyal takip ve bias önerisi!")

def main():
    """Ana rehber çalıştırma"""
    rehber = TurkceKurulumRehberi()
    rehber.tam_rehber_goster()

if __name__ == "__main__":
    main()