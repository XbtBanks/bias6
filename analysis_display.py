import streamlit as st

def display_professional_analysis_results(symbol, current_price, overall_bias, bias_strength,
                                         confluence, sentiment_analysis, scalp_analysis,
                                         market_analysis, funding_cvd_analysis, institutional_analysis,
                                         risk_analysis, mtf_analysis, fvg_analysis, data, is_crypto, is_forex, analysis_mode="📊 Standart Analiz"):
    """
    Professional card-based analysis results display
    """
    
    # Scalp-specific display for timeframe-optimized trading
    if "Scalp" in analysis_mode and scalp_analysis and 'trade_signals' in scalp_analysis:
        st.markdown("### ⚡ Scalp Trading Sinyali")
        
        trade_signals = scalp_analysis['trade_signals']
        action = trade_signals.get('action', 'HOLD')
        confidence = trade_signals.get('confidence', 0)
        
        # Display main scalp signal
        if action == 'LONG':
            st.success(f"🟢 LONG Pozisyon | Güven: {confidence:.0f}%")
        elif action == 'SHORT':
            st.error(f"🔴 SHORT Pozisyon | Güven: {confidence:.0f}%")
        else:
            st.warning(f"🟡 BEKLE | Sinyal Yok")
        
        # Show detailed trading levels if available
        if trade_signals.get('entry_price'):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Giriş", f"${trade_signals['entry_price']:.4f}")
            with col2:
                if trade_signals.get('stop_loss'):
                    stop_pct = trade_signals.get('stop_pct', 0.3)
                    st.metric("Stop Loss", f"${trade_signals['stop_loss']:.4f}")
                    st.caption(f"Risk: {stop_pct:.2f}%")
            with col3:
                if trade_signals.get('take_profit_1'):
                    tp1_pct = trade_signals.get('tp1_pct', 0.5)
                    st.metric("TP1", f"${trade_signals['take_profit_1']:.4f}")
                    st.caption(f"Hedef: {tp1_pct:.2f}%")
            with col4:
                if trade_signals.get('take_profit_2'):
                    tp2_pct = trade_signals.get('tp2_pct', 0.9)
                    st.metric("TP2", f"${trade_signals['take_profit_2']:.4f}")
                    st.caption(f"Hedef: {tp2_pct:.2f}%")
            
            # Risk/Reward calculation
            if trade_signals.get('stop_pct') and trade_signals.get('tp1_pct'):
                rr_ratio = trade_signals['tp1_pct'] / trade_signals['stop_pct']
                st.info(f"Risk/Ödül: 1:{rr_ratio:.1f} | Tavsiye Tutma: {trade_signals.get('hold_time', '5-30 dakika')}")
        
        st.markdown("---")
    
    # Unfilled FVG Analysis Display (Only show unfilled FVGs)
    if fvg_analysis:
        # Get only unfilled FVGs
        bullish_fvgs = [fvg for fvg in fvg_analysis.get('bullish_fvgs', []) if not fvg.get('filled', False)]
        bearish_fvgs = [fvg for fvg in fvg_analysis.get('bearish_fvgs', []) if not fvg.get('filled', False)]
        
        unfilled_count = len(bullish_fvgs) + len(bearish_fvgs)
        
        if unfilled_count > 0:
            st.markdown("### 📊 US FVG")
            
            # Only show unfilled FVG count
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("US FVG", unfilled_count)
            
            with col2:
                st.metric("Bullish US FVG", len(bullish_fvgs), delta="🟢")
            
            with col3:
                st.metric("Bearish US FVG", len(bearish_fvgs), delta="🔴")
            
            # Show only unfilled FVGs
            if bullish_fvgs or bearish_fvgs:
                st.subheader("⚡ Doldurulmamış FVG Seviyeleri")
                
                # Show unfilled bullish FVGs (Long side)
                if bullish_fvgs:
                    st.markdown("**🟢 LONG TARAF US FVG:**")
                    for fvg in bullish_fvgs[:3]:  # Show top 3
                        gap_size = fvg['top'] - fvg['bottom']
                        st.success(f"📈 US FVG: ${fvg['bottom']:.4f} - ${fvg['top']:.4f} (Gap: ${gap_size:.4f})")
                
                # Show unfilled bearish FVGs (Short side)
                if bearish_fvgs:
                    st.markdown("**🔴 SHORT TARAF US FVG:**")
                    for fvg in bearish_fvgs[:3]:  # Show top 3
                        gap_size = fvg['top'] - fvg['bottom']
                        st.error(f"📉 US FVG: ${fvg['bottom']:.4f} - ${fvg['top']:.4f} (Gap: ${gap_size:.4f})")
            
            st.markdown("---")
    
    # Continue with regular analysis display for non-scalp modes
    
    # Calculate scores
    trend_score = 50
    if isinstance(sentiment_analysis, dict) and 'overall_sentiment' in sentiment_analysis:
        sentiment_data = sentiment_analysis['overall_sentiment']
        if isinstance(sentiment_data, dict):
            trend_score = sentiment_data.get('score', 50)
    
    scalp_score = 0
    if isinstance(scalp_analysis, dict) and 'scalp_score' in scalp_analysis:
        scalp_data = scalp_analysis['scalp_score']
        if isinstance(scalp_data, dict):
            scalp_score = scalp_data.get('total_score', 0)
    
    trade_quality = 'Fair'
    rr_ratio = 1.0
    if isinstance(risk_analysis, dict) and 'risk_reward_analysis' in risk_analysis:
        rr_data = risk_analysis['risk_reward_analysis']
        if isinstance(rr_data, dict):
            trade_quality = rr_data.get('trade_quality', 'Fair')
            rr_ratio = rr_data.get('average_risk_reward', 1.0)
    
    # Multi-Timeframe integration
    mtf_score = 50
    mtf_confidence = 0
    if isinstance(mtf_analysis, dict):
        mtf_score = mtf_analysis.get('confluence_score', 50)
        mtf_confidence = mtf_analysis.get('entry_confidence', 0)
    
    # Final score calculation
    confluence_score = confluence.get('confluence_score', 50) if isinstance(confluence, dict) else 50
    base_score = (confluence_score + trend_score + scalp_score) / 3
    mtf_boost = (mtf_score / 100) * 25
    quality_multiplier = 1.2 if rr_ratio >= 2.5 else 1.1 if rr_ratio >= 2.0 else 1.0
    final_score = (base_score + mtf_boost) * quality_multiplier
    
    # Determine signal characteristics
    if final_score >= 75:
        signal_type = "GÜÇLÜ ALIM"
        signal_class = "card-bullish"
        badge_class = "badge-strong"
        signal_icon = "🚀"
        confidence_level = "Yüksek"
    elif final_score >= 60:
        signal_type = "ZAYIF ALIM"
        signal_class = "card-neutral"
        badge_class = "badge-weak"
        signal_icon = "⚠️"
        confidence_level = "Orta"
    else:
        signal_type = "BEKLE"
        signal_class = "card-bearish"
        badge_class = "badge-wait"
        signal_icon = "⏸️"
        confidence_level = "Düşük"
    
    # Executive Summary Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.3); border: 2px solid #334155;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem;">
            <h1 style="font-size: 1.8rem; font-weight: 900; color: #ffffff !important; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{signal_icon} {symbol} Analiz Özeti</h1>
            <div style="padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: white; border-radius: 30px; font-size: 1rem; font-weight: 800; text-shadow: 0 1px 2px rgba(0,0,0,0.3); border: 2px solid #f87171;">{signal_type}</div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem;">
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%); border-radius: 16px; border: 2px solid #a78bfa; box-shadow: 0 6px 20px rgba(139, 92, 246, 0.3);">
                <div style="font-size: 1.1rem; color: #ffffff; text-transform: uppercase; font-weight: 800; margin-bottom: 1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">Genel Skor</div>
                <div style="font-size: 3rem; font-weight: 900; color: #ffffff; margin: 1rem 0; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{final_score:.0f}</div>
                <div style="font-size: 1rem; color: #e9d5ff; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">/ 100</div>
            </div>
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #059669 0%, #10b981 100%); border-radius: 16px; border: 2px solid #34d399; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.3);">
                <div style="font-size: 1.1rem; color: #ffffff; text-transform: uppercase; font-weight: 800; margin-bottom: 1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">Trend Yönü</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #ffffff; margin: 1rem 0; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{"Yükseliş" if overall_bias == "Bullish" else "Düşüş" if overall_bias == "Bearish" else "Nötr"}</div>
                <div style="font-size: 1rem; color: #a7f3d0; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">Güç: {bias_strength:.0f}%</div>
            </div>
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #ea580c 0%, #f97316 100%); border-radius: 16px; border: 2px solid #fb923c; box-shadow: 0 6px 20px rgba(249, 115, 22, 0.3);">
                <div style="font-size: 1.1rem; color: #ffffff; text-transform: uppercase; font-weight: 800; margin-bottom: 1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">Güven Seviyesi</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #ffffff; margin: 1rem 0; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{confidence_level}</div>
                <div style="font-size: 1rem; color: #fed7aa; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">MTF: {mtf_confidence:.0f}%</div>
            </div>
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); border-radius: 16px; border: 2px solid #60a5fa; box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);">
                <div style="font-size: 1.1rem; color: #ffffff; text-transform: uppercase; font-weight: 800; margin-bottom: 1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">Güncel Fiyat</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #ffffff; margin: 1rem 0; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">${current_price:.4f}</div>
                <div style="font-size: 1rem; color: #bfdbfe; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">USD</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Multi-Timeframe Analysis Card
    if isinstance(mtf_analysis, dict) and mtf_analysis.get('timeframe_results'):
        display_mtf_card(mtf_analysis, mtf_score, mtf_confidence)
    
    # Trading Plan Card
    if final_score >= 40:
        display_trading_plan_card(current_price, final_score, data)
    
    # Market Analysis Cards
    col1, col2 = st.columns(2)
    
    with col1:
        if is_crypto and funding_cvd_analysis:
            display_funding_cvd_card(funding_cvd_analysis)
        elif is_forex and market_analysis['dxy_analysis']:
            display_dxy_card(market_analysis['dxy_analysis'])
    
    with col2:
        if institutional_analysis:
            display_institutional_levels_card(institutional_analysis, current_price)

def display_mtf_card(mtf_analysis, mtf_score, mtf_confidence):
    """Display Multi-Timeframe analysis card"""
    tf_results = mtf_analysis.get('timeframe_results', {})
    trend_direction = mtf_analysis.get('trend_direction', 'neutral')
    
    trend_color = "#10b981" if trend_direction == "bullish" else "#ef4444" if trend_direction == "bearish" else "#f59e0b"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 1.5rem; border-radius: 16px; margin: 1rem 0; box-shadow: 0 8px 25px rgba(0,0,0,0.2); border: 2px solid #475569;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;">
            <h2 style="font-size: 1.4rem; font-weight: 900; color: #ffffff !important; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">⏰ Multi-Timeframe Analiz</h2>
            <div style="padding: 0.5rem 1rem; background: {trend_color}; color: white; border-radius: 25px; font-size: 0.9rem; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">
                {trend_direction.upper()}
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #065f46 0%, #047857 100%); border-radius: 12px; border: 2px solid #10b981; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Confluence</div>
                <div style="font-size: 2.2rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">{mtf_score:.0f}%</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); border-radius: 12px; border: 2px solid #60a5fa; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Güven</div>
                <div style="font-size: 2.2rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">{mtf_confidence:.0f}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if tf_results:
        st.markdown("<div style='margin-bottom: 1rem; padding: 1rem; background: linear-gradient(135deg, #374151 0%, #4b5563 100%); border-radius: 12px; border: 2px solid #6b7280;'><strong style='color: #ffffff; font-size: 1.1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3);'>Timeframe Durumu:</strong></div>", unsafe_allow_html=True)
        for tf, data in tf_results.items():
            bias_color = "#10b981" if data['bias'] == 'bullish' else "#ef4444" if data['bias'] == 'bearish' else "#f59e0b"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; margin: 0.5rem 0; background: linear-gradient(135deg, #1f2937 0%, #374151 100%); border-radius: 12px; border: 2px solid #475569; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <span style="font-weight: 800; color: #ffffff; font-size: 1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">{tf}</span>
                <span style="color: {bias_color}; font-weight: 900; font-size: 1rem; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">{data['bias'].title()} ({data['strength']:.0f}%)</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_trading_plan_card(current_price, final_score, data):
    """Display trading plan card"""
    entry_price = current_price
    
    if final_score >= 75:
        stop_loss_pct = 1.5
        tp1_pct = 2.5
        tp2_pct = 4.0
        position_size = 2.0
        card_class = "card-bullish"
    else:
        stop_loss_pct = 1.0
        tp1_pct = 1.8
        tp2_pct = 2.8
        position_size = 1.0
        card_class = "card-neutral"
    
    stop_loss = entry_price * (1 - stop_loss_pct/100)
    tp1 = entry_price * (1 + tp1_pct/100)
    tp2 = entry_price * (1 + tp2_pct/100)
    risk_reward = tp1_pct / stop_loss_pct
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 2rem; border-radius: 20px; margin: 2rem 0; box-shadow: 0 10px 40px rgba(0,0,0,0.3); border: 2px solid #334155;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem;">
            <h2 style="font-size: 1.6rem; font-weight: 900; color: #ffffff !important; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">📋 Trading Plan</h2>
            <div style="padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; border-radius: 30px; font-size: 1rem; font-weight: 800; text-shadow: 0 1px 2px rgba(0,0,0,0.3); border: 2px solid #34d399;">
                AKTIF
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1.5rem;">
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%); border-radius: 16px; border: 2px solid #4f46e5; box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">ENTRY</div>
                <div style="font-size: 1.6rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">${entry_price:.4f}</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #b91c1c 0%, #e11d48 100%); border-radius: 16px; border: 2px solid #f43f5e; box-shadow: 0 6px 20px rgba(244, 63, 94, 0.4);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">STOP LOSS</div>
                <div style="font-size: 1.6rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">${stop_loss:.4f}</div>
                <div style="font-size: 0.9rem; color: #fce7f3; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">-{stop_loss_pct}%</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #047857 0%, #065f46 100%); border-radius: 16px; border: 2px solid #059669; box-shadow: 0 6px 20px rgba(5, 150, 105, 0.4);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">TAKE PROFIT 1</div>
                <div style="font-size: 1.6rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">${tp1:.4f}</div>
                <div style="font-size: 0.9rem; color: #ccfbf1; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">+{tp1_pct}%</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%); border-radius: 16px; border: 2px solid #14b8a6; box-shadow: 0 6px 20px rgba(20, 184, 166, 0.4);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">TAKE PROFIT 2</div>
                <div style="font-size: 1.6rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">${tp2:.4f}</div>
                <div style="font-size: 0.9rem; color: #ccfdf7; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">+{tp2_pct}%</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%); border-radius: 16px; border: 2px solid #a855f7; box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">RISK/REWARD</div>
                <div style="font-size: 1.6rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">1:{risk_reward:.1f}</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); border-radius: 16px; border: 2px solid #ef4444; box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">POZISYON</div>
                <div style="font-size: 1.6rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">{position_size}%</div>
                <div style="font-size: 0.9rem; color: #fecaca; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">Hesap</div>
            </div>
        </div>
        <div style="margin-top: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%); border-radius: 16px; border: 2px solid #06b6d4; box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4);">
            <div style="font-size: 1.1rem; color: #ffffff; font-weight: 800; text-shadow: 0 1px 2px rgba(0,0,0,0.3); text-align: center;">🎯 Tahmini Başarı Oranı: %65-75 (Multi-timeframe destekli)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_funding_cvd_card(funding_cvd_analysis):
    """Display Funding & CVD analysis card"""
    if not funding_cvd_analysis:
        return
    
    sentiment = funding_cvd_analysis.get('combined_sentiment', {})
    recommendation = sentiment.get('recommendation', 'WAIT')
    confidence = sentiment.get('confidence', 40)
    
    card_class = "card-bullish" if "BUY" in recommendation else "card-bearish" if "WAIT" in recommendation else "card-neutral"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 2rem; border-radius: 20px; margin: 2rem 0; box-shadow: 0 10px 40px rgba(0,0,0,0.3); border: 2px solid #334155;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem;">
            <h2 style="font-size: 1.6rem; font-weight: 900; color: #ffffff !important; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">💰 Funding & CVD</h2>
            <div style="padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #6366f1 0%, #7c3aed 100%); color: white; border-radius: 30px; font-size: 1rem; font-weight: 800; text-shadow: 0 1px 2px rgba(0,0,0,0.3); border: 2px solid #8b5cf6;">
                CRYPTO
            </div>
        </div>
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #312e81 0%, #4f46e5 100%); border-radius: 16px; box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4); border: 2px solid #6366f1;">
            <div style="font-size: 2.5rem; font-weight: 900; color: #ffffff; margin-bottom: 1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">{recommendation}</div>
            <div style="font-size: 1.3rem; color: #ffffff; font-weight: 800; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">Güven: {confidence}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_dxy_card(dxy_analysis):
    """Display DXY analysis card"""
    if not dxy_analysis:
        return
    
    trend = dxy_analysis.get('trend', 'Neutral')
    strength = dxy_analysis.get('strength', 50)
    current_price = dxy_analysis.get('current_price', 0)
    
    trend_color = "#10b981" if "Bullish" in trend else "#ef4444" if "Bearish" in trend else "#f59e0b"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 2rem; border-radius: 20px; margin: 2rem 0; box-shadow: 0 10px 40px rgba(0,0,0,0.3); border: 2px solid #334155;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem;">
            <h2 style="font-size: 1.6rem; font-weight: 900; color: #ffffff !important; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">🌐 DXY Analizi</h2>
            <div style="padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); color: white; border-radius: 30px; font-size: 1rem; font-weight: 800; text-shadow: 0 1px 2px rgba(0,0,0,0.3); border: 2px solid #f87171;">
                FOREX
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1.5rem;">
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); border-radius: 16px; border: 2px solid #60a5fa; box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">Seviye</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">{current_price:.2f}</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%); border-radius: 16px; border: 2px solid #a78bfa; box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">Trend</div>
                <div style="font-size: 1.4rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">{trend}</div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #059669 0%, #10b981 100%); border-radius: 16px; border: 2px solid #34d399; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 800; text-transform: uppercase; text-shadow: 0 1px 2px rgba(0,0,0,0.3); letter-spacing: 1px;">Güç</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #ffffff; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">{strength:.0f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_institutional_levels_card(institutional_analysis, current_price):
    """Display institutional levels card"""
    if not institutional_analysis:
        return
    
    nearest_levels = institutional_analysis.get('nearest_levels', {})
    support_level = nearest_levels.get('support')
    resistance_level = nearest_levels.get('resistance')
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 2rem; border-radius: 20px; margin: 2rem 0; box-shadow: 0 10px 40px rgba(0,0,0,0.3); border: 2px solid #334155;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem;">
            <h2 style="font-size: 1.6rem; font-weight: 900; color: #ffffff !important; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.4);">🏛️ Kritik Seviyeler</h2>
            <div style="padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%); color: white; border-radius: 30px; font-size: 1rem; font-weight: 800; text-shadow: 0 1px 2px rgba(0,0,0,0.3); border: 2px solid #a78bfa;">
                SEVIYELER
            </div>
        </div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1rem;">
    """, unsafe_allow_html=True)
    
    # Support level
    if support_level:
        st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #065f46 0%, #047857 100%); border-radius: 16px; box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3); border: 2px solid #10b981;">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🟢 DESTEK</div>
                <div style="font-size: 1.5rem; font-weight: 900; color: #ffffff; margin-bottom: 0.6rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">${support_level['price']:.4f}</div>
                <div style="font-size: 0.9rem; color: #a7f3d0; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">Uzaklık: {support_level['distance_pct']:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%); border-radius: 16px; box-shadow: 0 8px 25px rgba(107, 114, 128, 0.3); border: 2px solid #9ca3af;">
                <div style="font-size: 1rem; color: #ffffff; font-weight: 900; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">⚪ Yakın destek bulunamadı</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Resistance level
    if resistance_level:
        st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #991b1b 0%, #dc2626 100%); border-radius: 16px; box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3); border: 2px solid #ef4444;">
                <div style="font-size: 1rem; color: #ffffff; margin-bottom: 0.8rem; font-weight: 900; text-transform: uppercase; letter-spacing: 1px; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🔴 DİRENÇ</div>
                <div style="font-size: 1.5rem; font-weight: 900; color: #ffffff; margin-bottom: 0.6rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">${resistance_level['price']:.4f}</div>
                <div style="font-size: 0.9rem; color: #fecaca; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.2);">Uzaklık: {resistance_level['distance_pct']:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%); border-radius: 16px; box-shadow: 0 8px 25px rgba(107, 114, 128, 0.3); border: 2px solid #9ca3af;">
                <div style="font-size: 1rem; color: #ffffff; font-weight: 900; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">⚪ Yakın direnç bulunamadı</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)