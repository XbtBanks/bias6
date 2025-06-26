#!/bin/bash
# TradingView Integration Deployment Script

echo "Setting up FinansLab with TradingView integration..."

# Set environment variables
export TRADINGVIEW_USERNAME="your_email@domain.com"
export TRADINGVIEW_PASSWORD="your_password"

# Test connectivity
echo "Testing TradingView connectivity..."
python3 tradingview_diagnosis.py

# Test authentication
echo "Testing TradingView authentication..."
python3 tradingview_authenticated_fetcher.py

# Run the application
echo "Starting FinansLab application..."
streamlit run app.py --server.port 5000

echo "Setup complete! TradingView integration active."
