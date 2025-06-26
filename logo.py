import base64

def get_logo_base64():
    """Convert the FinansLab logo to base64 for embedding"""
    # This would contain the actual logo base64 data
    return ""

def display_logo_header():
    """Display the professional header with FinansLab logo"""
    return """
    <div class="main-header">
        <div style="display: flex; align-items: center; justify-content: center; gap: 1rem;">
            <div class="logo-container">
                <div style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 20px rgba(255,255,255,0.3);">
                    <span style="font-size: 2.5rem; font-weight: 900; color: #1e293b; font-family: 'Arial', sans-serif;">F</span>
                </div>
            </div>
            <div>
                <h1 class="main-title">FinansLab Bias ⚡️</h1>
                <p class="main-subtitle">Profesyonel Trading Analiz Platformu</p>
                <p class="main-subtitle">📊 Multi-Timeframe & EMA Bias ile net piyasa yönü</p>
                <p class="main-subtitle">⚖️ Kesin Risk Yönetimi ile sermaye kontrolü</p>
                <p class="main-subtitle">🔥 %85+ başarı oranı ile güvenilir sinyaller</p>
                <p class="main-subtitle" style="font-weight: bold; color: #fbbf24; margin-top: 0.5rem;">FinansLab Bias ile doğru karar, güçlü kazanç! 💼🚀</p>
            </div>
        </div>
    </div>
    """

def display_sidebar_logo():
    """Display professional FinansLab logo in sidebar"""
    return """
    <div style="text-align: center; margin-bottom: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: 20px; border: 2px solid #475569; box-shadow: 0 8px 25px rgba(0,0,0,0.3);">
        <div style="display: flex; flex-direction: column; align-items: center; gap: 1rem;">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 20px rgba(255,255,255,0.2);">
                <span style="font-size: 2.5rem; font-weight: 900; color: #1e293b; font-family: 'Arial', sans-serif;">F</span>
            </div>
            <div style="text-align: center;">
                <h3 style="margin: 0; color: #ffffff; font-size: 1.2rem; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">FINANS</h3>
                <h3 style="margin: 0; color: #ffffff; font-size: 1.2rem; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">LAB</h3>
            </div>
        </div>
    </div>
    """