import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

class InstitutionalLevels:
    """
    Institutional Level Detection System
    
    Automatically detects and tracks key institutional price levels:
    - Yearly/Quarterly/Monthly/Weekly/Daily Opens, Highs, Lows
    - Equilibrium levels (50% of range)
    - Previous period levels
    - Level strength and significance analysis
    """
    
    def __init__(self):
        self.timezone = pytz.timezone('UTC')
        
    def calculate_institutional_levels(self, data, current_timeframe='1h'):
        """
        Calculate all institutional levels for the given data
        
        Args:
            data (pd.DataFrame): OHLCV data with datetime index
            current_timeframe (str): Current analysis timeframe
            
        Returns:
            dict: Comprehensive institutional levels analysis
        """
        if data.empty:
            return self._get_fallback_levels()
            
        try:
            # Ensure datetime index
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)
                
            current_price = data['Close'].iloc[-1]
            current_time = data.index[-1]
            
            # Calculate all timeframe levels
            levels = {
                'yearly': self._calculate_yearly_levels(data, current_time),
                'quarterly': self._calculate_quarterly_levels(data, current_time),
                'monthly': self._calculate_monthly_levels(data, current_time),
                'weekly': self._calculate_weekly_levels(data, current_time),
                'daily': self._calculate_daily_levels(data, current_time),
                'session': self._calculate_session_levels(data, current_time)
            }
            
            # Find nearest levels to current price
            nearest_levels = self._find_nearest_levels(levels, current_price)
            
            # Analyze level strength and significance
            level_analysis = self._analyze_level_strength(data, levels, current_price)
            
            # Generate trading insights
            trading_insights = self._generate_level_insights(levels, current_price, level_analysis)
            
            return {
                'levels': levels,
                'nearest_levels': nearest_levels,
                'level_analysis': level_analysis,
                'trading_insights': trading_insights,
                'current_price': current_price,
                'last_updated': current_time.strftime('%Y-%m-%d %H:%M:%S UTC')
            }
            
        except Exception as e:
            print(f"Error calculating institutional levels: {e}")
            return self._get_fallback_levels()
    
    def _calculate_yearly_levels(self, data, current_time):
        """Calculate yearly levels (current and previous year)"""
        year_start = datetime(current_time.year, 1, 1, tzinfo=self.timezone)
        prev_year_start = datetime(current_time.year - 1, 1, 1, tzinfo=self.timezone)
        prev_year_end = datetime(current_time.year - 1, 12, 31, 23, 59, 59, tzinfo=self.timezone)
        
        # Current year data
        current_year_data = data[data.index >= year_start]
        
        # Previous year data
        prev_year_data = data[(data.index >= prev_year_start) & (data.index <= prev_year_end)]
        
        levels = {}
        
        # Current year levels
        if not current_year_data.empty:
            levels['current'] = {
                'open': current_year_data['Open'].iloc[0],
                'high': current_year_data['High'].max(),
                'low': current_year_data['Low'].min(),
                'eq': (current_year_data['High'].max() + current_year_data['Low'].min()) / 2
            }
        
        # Previous year levels
        if not prev_year_data.empty:
            levels['previous'] = {
                'open': prev_year_data['Open'].iloc[0],
                'high': prev_year_data['High'].max(),
                'low': prev_year_data['Low'].min(),
                'eq': (prev_year_data['High'].max() + prev_year_data['Low'].min()) / 2
            }
        
        return levels
    
    def _calculate_quarterly_levels(self, data, current_time):
        """Calculate quarterly levels (current and previous quarter)"""
        # Determine current quarter
        quarter = (current_time.month - 1) // 3 + 1
        quarter_start_month = (quarter - 1) * 3 + 1
        
        quarter_start = datetime(current_time.year, quarter_start_month, 1, tzinfo=self.timezone)
        
        # Previous quarter
        if quarter == 1:
            prev_quarter_start = datetime(current_time.year - 1, 10, 1, tzinfo=self.timezone)
            prev_quarter_end = datetime(current_time.year - 1, 12, 31, 23, 59, 59, tzinfo=self.timezone)
        else:
            prev_quarter_month = (quarter - 2) * 3 + 1
            prev_quarter_start = datetime(current_time.year, prev_quarter_month, 1, tzinfo=self.timezone)
            prev_quarter_end = datetime(current_time.year, quarter_start_month - 1, 28, 23, 59, 59, tzinfo=self.timezone)
        
        # Current quarter data
        current_quarter_data = data[data.index >= quarter_start]
        
        # Previous quarter data
        prev_quarter_data = data[(data.index >= prev_quarter_start) & (data.index <= prev_quarter_end)]
        
        levels = {}
        
        # Current quarter levels
        if not current_quarter_data.empty:
            levels['current'] = {
                'open': current_quarter_data['Open'].iloc[0],
                'high': current_quarter_data['High'].max(),
                'low': current_quarter_data['Low'].min(),
                'eq': (current_quarter_data['High'].max() + current_quarter_data['Low'].min()) / 2
            }
        
        # Previous quarter levels
        if not prev_quarter_data.empty:
            levels['previous'] = {
                'open': prev_quarter_data['Open'].iloc[0],
                'high': prev_quarter_data['High'].max(),
                'low': prev_quarter_data['Low'].min(),
                'eq': (prev_quarter_data['High'].max() + prev_quarter_data['Low'].min()) / 2
            }
        
        return levels
    
    def _calculate_monthly_levels(self, data, current_time):
        """Calculate monthly levels (current and previous month)"""
        month_start = datetime(current_time.year, current_time.month, 1, tzinfo=self.timezone)
        
        # Previous month
        if current_time.month == 1:
            prev_month_start = datetime(current_time.year - 1, 12, 1, tzinfo=self.timezone)
            prev_month_end = datetime(current_time.year - 1, 12, 31, 23, 59, 59, tzinfo=self.timezone)
        else:
            prev_month_start = datetime(current_time.year, current_time.month - 1, 1, tzinfo=self.timezone)
            # Get last day of previous month
            next_month = month_start
            prev_month_end = next_month - timedelta(seconds=1)
        
        # Current month data
        current_month_data = data[data.index >= month_start]
        
        # Previous month data
        prev_month_data = data[(data.index >= prev_month_start) & (data.index <= prev_month_end)]
        
        levels = {}
        
        # Current month levels
        if not current_month_data.empty:
            levels['current'] = {
                'open': current_month_data['Open'].iloc[0],
                'high': current_month_data['High'].max(),
                'low': current_month_data['Low'].min(),
                'eq': (current_month_data['High'].max() + current_month_data['Low'].min()) / 2
            }
        
        # Previous month levels
        if not prev_month_data.empty:
            levels['previous'] = {
                'open': prev_month_data['Open'].iloc[0],
                'high': prev_month_data['High'].max(),
                'low': prev_month_data['Low'].min(),
                'eq': (prev_month_data['High'].max() + prev_month_data['Low'].min()) / 2
            }
        
        return levels
    
    def _calculate_weekly_levels(self, data, current_time):
        """Calculate weekly levels (current and previous week)"""
        # Get Monday of current week
        days_since_monday = current_time.weekday()
        week_start = current_time - timedelta(days=days_since_monday)
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Previous week
        prev_week_start = week_start - timedelta(days=7)
        prev_week_end = week_start - timedelta(seconds=1)
        
        # Current week data
        current_week_data = data[data.index >= week_start]
        
        # Previous week data
        prev_week_data = data[(data.index >= prev_week_start) & (data.index <= prev_week_end)]
        
        levels = {}
        
        # Current week levels
        if not current_week_data.empty:
            levels['current'] = {
                'open': current_week_data['Open'].iloc[0],
                'high': current_week_data['High'].max(),
                'low': current_week_data['Low'].min(),
                'eq': (current_week_data['High'].max() + current_week_data['Low'].min()) / 2
            }
        
        # Previous week levels
        if not prev_week_data.empty:
            levels['previous'] = {
                'open': prev_week_data['Open'].iloc[0],
                'high': prev_week_data['High'].max(),
                'low': prev_week_data['Low'].min(),
                'eq': (prev_week_data['High'].max() + prev_week_data['Low'].min()) / 2
            }
        
        return levels
    
    def _calculate_daily_levels(self, data, current_time):
        """Calculate daily levels (current and previous day)"""
        day_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        prev_day_start = day_start - timedelta(days=1)
        prev_day_end = day_start - timedelta(seconds=1)
        
        # Current day data
        current_day_data = data[data.index >= day_start]
        
        # Previous day data
        prev_day_data = data[(data.index >= prev_day_start) & (data.index <= prev_day_end)]
        
        levels = {}
        
        # Current day levels
        if not current_day_data.empty:
            levels['current'] = {
                'open': current_day_data['Open'].iloc[0],
                'high': current_day_data['High'].max(),
                'low': current_day_data['Low'].min(),
                'eq': (current_day_data['High'].max() + current_day_data['Low'].min()) / 2
            }
        
        # Previous day levels
        if not prev_day_data.empty:
            levels['previous'] = {
                'open': prev_day_data['Open'].iloc[0],
                'high': prev_day_data['High'].max(),
                'low': prev_day_data['Low'].min(),
                'eq': (prev_day_data['High'].max() + prev_day_data['Low'].min()) / 2
            }
        
        return levels
    
    def _calculate_session_levels(self, data, current_time):
        """Calculate trading session levels (Asia, London, US)"""
        # Session times in UTC
        sessions = {
            'asia': {'start': 23, 'end': 8},      # 23:00-08:00 UTC
            'london': {'start': 8, 'end': 16},    # 08:00-16:00 UTC  
            'us': {'start': 13, 'end': 22}        # 13:00-22:00 UTC (overlaps with London)
        }
        
        levels = {}
        
        for session_name, session_times in sessions.items():
            # Get today's session data
            today = current_time.date()
            session_start = datetime.combine(today, datetime.min.time().replace(hour=session_times['start']))
            session_start = session_start.replace(tzinfo=self.timezone)
            
            if session_times['end'] < session_times['start']:  # Asia session crosses midnight
                session_end = session_start + timedelta(days=1)
                session_end = session_end.replace(hour=session_times['end'])
            else:
                session_end = session_start.replace(hour=session_times['end'])
            
            session_data = data[(data.index >= session_start) & (data.index <= session_end)]
            
            if not session_data.empty:
                levels[session_name] = {
                    'open': session_data['Open'].iloc[0],
                    'high': session_data['High'].max(),
                    'low': session_data['Low'].min(),
                    'eq': (session_data['High'].max() + session_data['Low'].min()) / 2
                }
        
        return levels
    
    def _find_nearest_levels(self, levels, current_price):
        """Find the nearest support and resistance levels to current price"""
        all_levels = []
        
        # Collect all levels with their metadata
        for timeframe, timeframe_data in levels.items():
            for period, period_data in timeframe_data.items():
                if isinstance(period_data, dict):
                    for level_type, level_value in period_data.items():
                        if isinstance(level_value, (int, float)) and not np.isnan(level_value):
                            all_levels.append({
                                'price': level_value,
                                'timeframe': timeframe,
                                'period': period,
                                'type': level_type,
                                'distance': abs(level_value - current_price),
                                'distance_pct': abs(level_value - current_price) / current_price * 100
                            })
        
        # Sort by distance from current price
        all_levels.sort(key=lambda x: x['distance'])
        
        # Find nearest support and resistance
        nearest_support = None
        nearest_resistance = None
        
        for level in all_levels:
            if level['price'] < current_price and nearest_support is None:
                nearest_support = level
            elif level['price'] > current_price and nearest_resistance is None:
                nearest_resistance = level
            
            if nearest_support and nearest_resistance:
                break
        
        return {
            'support': nearest_support,
            'resistance': nearest_resistance,
            'all_nearby': all_levels[:10]  # Top 10 nearest levels
        }
    
    def _analyze_level_strength(self, data, levels, current_price):
        """Analyze the strength and significance of levels"""
        analysis = {
            'key_levels': [],
            'confluence_zones': [],
            'level_importance': {}
        }
        
        # Weight levels by timeframe importance
        timeframe_weights = {
            'yearly': 5.0,
            'quarterly': 4.0,
            'monthly': 3.0,
            'weekly': 2.0,
            'daily': 1.0,
            'session': 0.5
        }
        
        # Weight levels by type importance
        type_weights = {
            'high': 2.0,
            'low': 2.0,
            'open': 1.5,
            'eq': 1.0
        }
        
        # Collect all weighted levels
        weighted_levels = []
        
        for timeframe, timeframe_data in levels.items():
            tf_weight = timeframe_weights.get(timeframe, 1.0)
            
            for period, period_data in timeframe_data.items():
                if isinstance(period_data, dict):
                    for level_type, level_value in period_data.items():
                        if isinstance(level_value, (int, float)) and not np.isnan(level_value):
                            type_weight = type_weights.get(level_type, 1.0)
                            total_weight = tf_weight * type_weight
                            
                            weighted_levels.append({
                                'price': level_value,
                                'weight': total_weight,
                                'timeframe': timeframe,
                                'period': period,
                                'type': level_type,
                                'distance_pct': abs(level_value - current_price) / current_price * 100
                            })
        
        # Sort by weight (importance)
        weighted_levels.sort(key=lambda x: x['weight'], reverse=True)
        
        # Identify key levels (top 10 by weight)
        analysis['key_levels'] = weighted_levels[:10]
        
        # Find confluence zones (levels within 1% of each other)
        confluence_zones = []
        processed_levels = set()
        
        for i, level in enumerate(weighted_levels):
            if i in processed_levels:
                continue
                
            zone_levels = [level]
            processed_levels.add(i)
            
            for j, other_level in enumerate(weighted_levels[i+1:], i+1):
                if j in processed_levels:
                    continue
                    
                price_diff_pct = abs(level['price'] - other_level['price']) / level['price'] * 100
                
                if price_diff_pct <= 1.0:  # Within 1%
                    zone_levels.append(other_level)
                    processed_levels.add(j)
            
            if len(zone_levels) >= 2:  # At least 2 levels for confluence
                avg_price = sum(l['price'] for l in zone_levels) / len(zone_levels)
                total_weight = sum(l['weight'] for l in zone_levels)
                
                confluence_zones.append({
                    'price': avg_price,
                    'weight': total_weight,
                    'level_count': len(zone_levels),
                    'levels': zone_levels,
                    'distance_pct': abs(avg_price - current_price) / current_price * 100
                })
        
        # Sort confluence zones by weight
        confluence_zones.sort(key=lambda x: x['weight'], reverse=True)
        analysis['confluence_zones'] = confluence_zones[:5]  # Top 5 confluence zones
        
        return analysis
    
    def _generate_level_insights(self, levels, current_price, level_analysis):
        """Generate trading insights based on institutional levels"""
        insights = {
            'level_bias': 'Neutral',
            'key_support': None,
            'key_resistance': None,
            'confluence_analysis': [],
            'trading_recommendations': [],
            'risk_levels': []
        }
        
        # Find strongest confluence zone
        if level_analysis['confluence_zones']:
            strongest_confluence = level_analysis['confluence_zones'][0]
            
            if strongest_confluence['price'] > current_price:
                insights['key_resistance'] = strongest_confluence
                insights['level_bias'] = 'Bearish' if strongest_confluence['distance_pct'] < 2 else 'Neutral'
            else:
                insights['key_support'] = strongest_confluence
                insights['level_bias'] = 'Bullish' if strongest_confluence['distance_pct'] < 2 else 'Neutral'
        
        # Analyze confluence zones
        for zone in level_analysis['confluence_zones'][:3]:
            if zone['price'] > current_price:
                zone_type = 'Resistance'
                bias_impact = 'Bearish pressure'
            else:
                zone_type = 'Support'
                bias_impact = 'Bullish support'
            
            insights['confluence_analysis'].append({
                'type': zone_type,
                'price': zone['price'],
                'strength': 'Strong' if zone['weight'] > 8 else 'Moderate' if zone['weight'] > 4 else 'Weak',
                'levels_count': zone['level_count'],
                'distance_pct': zone['distance_pct'],
                'bias_impact': bias_impact
            })
        
        # Generate trading recommendations
        if insights['key_resistance'] and insights['key_resistance']['distance_pct'] < 1:
            insights['trading_recommendations'].append({
                'action': 'Dikkatli Ol - Güçlü Direnç Yakın',
                'reason': f"Fiyat {insights['key_resistance']['distance_pct']:.2f}% uzaklıkta güçlü direnç bölgesine yaklaşıyor",
                'level': insights['key_resistance']['price']
            })
        
        if insights['key_support'] and insights['key_support']['distance_pct'] < 1:
            insights['trading_recommendations'].append({
                'action': 'Alım Fırsatı - Güçlü Destek Yakın',
                'reason': f"Fiyat {insights['key_support']['distance_pct']:.2f}% uzaklıkta güçlü destek bölgesine yaklaşıyor",
                'level': insights['key_support']['price']
            })
        
        # Risk levels (closest high-weight levels)
        key_levels = level_analysis['key_levels'][:5]
        for level in key_levels:
            if level['distance_pct'] < 5:  # Within 5%
                level_type = 'Risk' if abs(level['price'] - current_price) / current_price > 0.02 else 'Critical'
                insights['risk_levels'].append({
                    'price': level['price'],
                    'type': level_type,
                    'timeframe': level['timeframe'],
                    'level_type': level['type'],
                    'distance_pct': level['distance_pct']
                })
        
        return insights
    
    def _get_fallback_levels(self):
        """Fallback levels when calculation fails"""
        return {
            'levels': {
                'yearly': {'current': {}, 'previous': {}},
                'monthly': {'current': {}, 'previous': {}},
                'weekly': {'current': {}, 'previous': {}},
                'daily': {'current': {}, 'previous': {}}
            },
            'nearest_levels': {'support': None, 'resistance': None, 'all_nearby': []},
            'level_analysis': {'key_levels': [], 'confluence_zones': []},
            'trading_insights': {
                'level_bias': 'Neutral',
                'confluence_analysis': [],
                'trading_recommendations': [{'action': 'Veri Yetersiz', 'reason': 'Kurumsal seviye analizi için yeterli veri yok'}],
                'risk_levels': []
            },
            'current_price': 0,
            'last_updated': 'N/A'
        }