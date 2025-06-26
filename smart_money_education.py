class SmartMoneyEducation:
    """
    Smart Money Educational Content Integration
    
    Provides educational insights and explanations for trading concepts
    based on the Smart Money curriculum covering 8 key modules.
    """
    
    def __init__(self):
        self.modules = {
            1: "Temel Yapı ve Kavramsal Omurga",
            2: "Fibonacci, Dönüş Seviyeleri ve Giriş Noktaları", 
            3: "Likidite, Tuzaklar ve Manipülasyon",
            4: "Destek-Direnç Dönüşümleri & Fiyat Hafızası",
            5: "Strateji Geliştirme ve Uygulama Mantığı",
            6: "Psikoloji, Risk ve İyileştirme Süreci",
            7: "Scalping, Zamanlama ve Mikro Yapılar",
            8: "Derinlik ve Uyum Mekanizmaları"
        }
        
        self.educational_content = self._initialize_content()
    
    def _initialize_content(self):
        return {
            "market_structure": {
                "title": "Market Yapısı ve Kurumsal Omurga",
                "content": """
                **Market Yapısı Nedir?**
                • Kurumsal oyuncuların fiyat hareketlerini nasıl yönlendirdiği
                • Order Block'ların oluşumu ve işlevi
                • Imbalance (Dengesizlik) alanlarının tespiti
                • Breaker Block'ların trend değişim sinyalleri
                """,
                "practical_tip": "Order Block'lar güçlü destek/direnç seviyeleridir. Fiyat bu alanlara döndüğünde reaksiyon bekleyin."
            },
            
            "fibonacci_entries": {
                "title": "Fibonacci ve Optimal Giriş Noktaları",
                "content": """
                **Fibonacci Seviyeleri:**
                • %23.6, %38.2, %50, %61.8, %78.6 retracement seviyeleri
                • BPR (Balanced Price Range) ile trend başlangıçları
                • Süper Girdap Etkisi Fibonacci kombinasyonları
                """,
                "practical_tip": "En güçlü giriş noktaları %61.8-78.6 arasındaki Fibonacci bölgesidir."
            },
            
            "liquidity_manipulation": {
                "title": "Likidite Tuzakları ve Manipülasyon",
                "content": """
                **Likidite Nasıl Çalışır?**
                • Stop Av Mekanizması (Stop Hunt)
                • SFP (Swing Failure Pattern) tuzakları
                • Likidite Kayıpları ve OB geçersizlikleri
                • Karar alma süreçlerinde manipülasyon etkisi
                """,
                "practical_tip": "Yüksek hacimli seviyelerin altında/üstünde stop loss koymayın. Bu alanlar likidite tuzağıdır."
            },
            
            "support_resistance": {
                "title": "Destek-Direnç Dönüşümleri",
                "content": """
                **Fiyat Hafızası Konsepti:**
                • Eski destek seviyeleri yeni direnç olur
                • FTR/FTB (Failure To Return/Break) formasyonları
                • Geçmiş dönemin önemli seviyeleri
                • Three Tap Concept (Üç Dokunuş Kuralı)
                """,
                "practical_tip": "Kırılan bir destek seviyesi, tekrar test edildiğinde güçlü direnç görevi görür."
            },
            
            "strategy_development": {
                "title": "Strateji Geliştirme Mantığı",
                "content": """
                **Klasik SMC Setapları:**
                • Tsfiran İlem Yapısı ve Önceleme
                • Trend Değişimlerini Önceden Görebilme
                • Kill Beklengarken Tehlimi Emre Yönlerin
                • Güçlü Smart Money Setapları
                """,
                "practical_tip": "Stratejinizi backtesting ile test edin. Geçmiş verilerde çalışmayan strateji canlı piyasada da çalışmaz."
            },
            
            "psychology_risk": {
                "title": "Trading Psikolojisi ve Risk Yönetimi",
                "content": """
                **Psikolojik Faktörler:**
                • Yüksek ve Düşük Olasılık İşlemleri
                • Trader için 10 Altın Kural
                • Üst Düzey Risk Yönetimi Teknikleri
                • Pozisyon Büyüklüğü Hesaplama
                • Portföy Risk Yönetimi
                """,
                "practical_tip": "Hesabınızın %2'sinden fazlasını tek işlemde riske atmayın. Bu altın kuraldır."
            },
            
            "scalping_micro": {
                "title": "Scalping ve Mikro Yapılar", 
                "content": """
                **Scalping Teknikleri:**
                • VWAP ile Mikro Alanı Scalping
                • Range ve Consolidation İle Temelli Girişler
                • Zamanlama ve Seansı Bazlı Scalping
                • En Etkili Zaman Dilimleri
                • İşlem Performansı ve Analizler
                """,
                "practical_tip": "Scalping için en iyi saatler: Londra açılışı (10:00-12:00) ve ABD açılışı (17:30-20:00)"
            },
            
            "depth_mechanics": {
                "title": "Derinlik ve Uyum Mekanizmaları",
                "content": """
                **Gelişmiş Analiz:**
                • OB (Order Block) Çalışması Geçercilik
                • Market Profil Santalyende SMC Ayrımları  
                • Algoritmik Yapıların OB ve Likidite Etkisi
                • Funding Rate, OI, CVD ile Yapısal Veri Okuma
                • SMC + Orderflow ile Üst Seviye Trade Uyumlaması
                """,
                "practical_tip": "CVD divergence + OB seviyesi = En güçlü sinyal kombinasyonu"
            }
        }
    
    def get_educational_tooltip(self, concept_key):
        """
        Get educational tooltip for specific trading concept
        """
        if concept_key in self.educational_content:
            content = self.educational_content[concept_key]
            return {
                'title': content['title'],
                'explanation': content['content'],
                'tip': content['practical_tip']
            }
        return None
    
    def get_context_aware_education(self, signal_type, market_condition):
        """
        Get context-aware educational content based on current market conditions
        """
        education_tips = []
        
        # Signal-specific education
        if signal_type == "strong_buy":
            education_tips.append({
                'module': 'Module 3: Likidite',
                'tip': "Güçlü alım sinyalinde bile likidite tuzaklarına dikkat edin. Stop hunt olabilir."
            })
            
        elif signal_type == "scalp_signal":
            education_tips.append({
                'module': 'Module 7: Scalping',
                'tip': "Scalp işlemlerinde 1-15 dakika arasında çıkın. Zamanlama kritiktir."
            })
            
        elif signal_type == "range_bound":
            education_tips.append({
                'module': 'Module 4: Destek-Direnç',
                'tip': "Range piyasasında destek ve direnç seviyeleri güçlüdür. Bounce bekleyin."
            })
        
        # Market condition education
        if market_condition == "high_volatility":
            education_tips.append({
                'module': 'Module 6: Risk Yönetimi',
                'tip': "Yüksek volatilitede position size'ınızı küçültün. Risk yönetimi öncelik."
            })
            
        elif market_condition == "trending":
            education_tips.append({
                'module': 'Module 2: Fibonacci',
                'tip': "Trend piyasasında Fibonacci %61.8 seviyesi güçlü destek/direnç."
            })
        
        return education_tips
    
    def get_risk_management_education(self, account_size, risk_percentage):
        """
        Get personalized risk management education
        """
        if risk_percentage > 5:
            return {
                'warning': "⚠️ Yüksek Risk Uyarısı",
                'education': "Module 6'ya göre tek işlemde %2'den fazla risk almayın. Bu kural portföyünüzü korur.",
                'recommendation': f"Önerilen risk: %2 = ${account_size * 0.02:.0f}"
            }
        elif risk_percentage > 2:
            return {
                'warning': "⚠️ Orta Risk",
                'education': "Kabul edilebilir risk seviyesi ama daha konservatif olabilirsiniz.",
                'recommendation': "Risk yönetimi kurallarına uygun"
            }
        else:
            return {
                'warning': "✅ İyi Risk Yönetimi",
                'education': "Module 6 prensipleri ile uyumlu risk seviyesi.",
                'recommendation': "Mükemmel risk kontrolü"
            }
    
    def get_session_based_education(self, current_session, performance_data):
        """
        Get session-based educational insights
        """
        session_education = {
            'Asya': {
                'characteristics': 'Düşük volatilite, range piyasaları',
                'strategy': 'Module 7: Scalping teknikleri tercih edin',
                'warning': 'Büyük pozisyonlardan kaçının'
            },
            'Londra': {
                'characteristics': 'Yüksek volatilite, trend başlangıçları',
                'strategy': 'Module 1: Market yapısı analizi yapın',
                'warning': 'İlk 2 saatte dikkatli olun'
            },
            'ABD Açılış': {
                'characteristics': 'En yüksek volatilite, güçlü trendler',
                'strategy': 'Module 5: Ana strateji setapları kullanın',
                'warning': 'Risk yönetimi kritik'
            },
            'ABD Kapanış': {
                'characteristics': 'Azalan volatilite, konsolidasyon',
                'strategy': 'Module 4: Destek/direnç takibi',
                'warning': 'Trend dönüşlerine hazır olun'
            }
        }
        
        if current_session in session_education:
            return session_education[current_session]
        
        return session_education['Londra']  # Default
    
    def get_smart_money_insights(self, market_data):
        """
        Get Smart Money specific insights based on current market data
        """
        insights = []
        
        # Order Block analysis
        insights.append({
            'concept': 'Order Block Analizi',
            'insight': 'Kurumsal seviyeler fiyat hafızası oluşturur. Bu seviyeler güçlü reaksiyon noktalarıdır.',
            'application': 'Mevcut fiyat seviyesinde Order Block var mı kontrol edin.'
        })
        
        # Imbalance detection
        insights.append({
            'concept': 'Imbalance (FVG) Tespiti', 
            'insight': 'Fiyat boşlukları doldurulma eğilimindedir. Bu alanlar mıknatıs görevi görür.',
            'application': 'Grafikteki gap alanlarını işaretleyin ve reaksiyon bekleyin.'
        })
        
        # Liquidity analysis
        insights.append({
            'concept': 'Likidite Analizi',
            'insight': 'Yüksek hacimli seviyeler likidite havuzudur. Kurumsal oyuncular bu alanları hedefler.',
            'application': 'Previous High/Low seviyelerinin altında/üstünde dikkatli olun.'
        })
        
        return insights
    
    def generate_educational_summary(self, user_performance):
        """
        Generate personalized educational recommendations based on user performance
        """
        recommendations = []
        
        # Win rate analysis
        if user_performance.get('win_rate', 50) < 40:
            recommendations.append({
                'focus_area': 'Module 1 & 3: Market Yapısı ve Likidite',
                'reason': 'Düşük kazanma oranı - temel analizi güçlendirin',
                'action': 'Order Block ve likidite seviyelerini daha dikkatli analiz edin'
            })
        
        # Risk/Reward analysis  
        if user_performance.get('avg_rr', 1) < 1.5:
            recommendations.append({
                'focus_area': 'Module 6: Risk Yönetimi',
                'reason': 'Düşük R/R oranı - hedefleri uzatın',
                'action': 'Take profit seviyelerini Fibonacci veya OB seviyelerine yerleştirin'
            })
        
        # Scalping performance
        if user_performance.get('scalp_success', 50) < 60:
            recommendations.append({
                'focus_area': 'Module 7: Scalping ve Zamanlama',
                'reason': 'Scalp performansı düşük - zamanlama iyileştirin',
                'action': 'Sadece Londra ve ABD açılış saatlerinde scalp yapın'
            })
        
        return recommendations