# FinansLab Bias - Automated Trading Signal System

Advanced AI-powered trading analysis platform providing intelligent market insights with full automation and Telegram integration.

## Features

- **EMA Bias Analysis**: 5-period EMA system (45, 89, 144, 200, 276)
- **Fair Value Gap Detection**: Automated US FVG pattern recognition
- **Scalp Trading Signals**: RSI pullback and MACD crossover strategies
- **Risk Management**: Automatic entry, stop-loss, and take-profit calculations
- **Telegram Integration**: Real-time signal notifications
- **Multi-Market Support**: Crypto, Forex, Commodities
- **Adaptive Scanning**: 5-15 minute intervals based on market sessions

## Supported Markets

- **Crypto**: BTC-USD, ETH-USD
- **Commodities**: GC=F (Gold Futures)
- **Forex**: EURUSD=X, GBPUSD=X, USDJPY=X

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/finanslab-bias.git
cd finanslab-bias
```

2. Install dependencies:
```bash
pip install -r app_requirements.txt
```

3. Set up environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export TELEGRAM_TOPIC_ID="your_topic_id"
```

4. Run the application:
```bash
streamlit run finanslab_unified.py --server.port 5000
```

## Telegram Setup

1. Create a bot with @BotFather on Telegram
2. Get your chat ID or group ID
3. Add the bot to your group/channel
4. Set environment variables or configure in the web interface

## Configuration

The system automatically adapts scanning intervals based on market sessions:
- **London-NY Overlap**: 5 minutes (peak activity)
- **London/NY Sessions**: 10 minutes
- **Quiet periods**: 15 minutes

## Signal Quality

Signals are rated using a 13-point confluence system:
- **MÜKEMMEL**: 9+ points (automatic Telegram notification)
- **ÇOK İYİ**: 7-8 points
- **İYİ**: 5-6 points

## Risk Management

- **Risk per trade**: 1% of account
- **Reward ratio**: 1.5R
- **Stop loss**: ATR-based calculation
- **Position sizing**: Automatic calculation

## Deployment

### Docker
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r app_requirements.txt
EXPOSE 5000
CMD ["streamlit", "run", "finanslab_unified.py", "--server.port=5000", "--server.address=0.0.0.0"]
```

### Heroku
1. Create `Procfile`:
```
web: streamlit run finanslab_unified.py --server.port=$PORT --server.address=0.0.0.0
```

2. Set config vars in Heroku dashboard

### VPS/Cloud Server
```bash
# Install Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-pip

# Clone and setup
git clone https://github.com/yourusername/finanslab-bias.git
cd finanslab-bias
pip3.11 install -r app_requirements.txt

# Run with screen or systemd
screen -S finanslab
streamlit run finanslab_unified.py --server.port 5000 --server.address 0.0.0.0
```

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

## Support

For support, join our Telegram group or create an issue on GitHub.