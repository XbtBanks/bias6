# Bot Stability Solutions

## Common Bot Shutdown Issues & Solutions

### 1. Memory Management
```python
import gc
import psutil

# Memory cleanup in main loop
def cleanup_memory():
    gc.collect()
    if psutil.virtual_memory().percent > 80:
        # Restart or clear cache
        pass
```

### 2. Error Handling
```python
import time
import logging

def robust_telegram_send(message):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Send message
            return True
        except Exception as e:
            logging.error(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return False
```

### 3. Keep-Alive System
```python
import threading
import time

def heartbeat():
    while True:
        try:
            # Send test ping
            requests.get("https://api.telegram.org/bot{token}/getMe")
            time.sleep(300)  # 5 minutes
        except:
            # Restart bot
            pass

# Start heartbeat thread
threading.Thread(target=heartbeat, daemon=True).start()
```

### 4. Auto-Restart Script
```bash
#!/bin/bash
while true; do
    python3 your_bot.py
    echo "Bot crashed, restarting in 10 seconds..."
    sleep 10
done
```

### 5. Process Manager (PM2)
```bash
# Install PM2
npm install -g pm2

# Start bot with PM2
pm2 start bot.py --interpreter python3 --name "finanslab-bot"

# Auto-restart on crash
pm2 startup
pm2 save
```

### 6. Docker Container
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "-u", "bot.py"]
# Add restart policy in docker-compose
```

### 7. Monitoring & Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
```

### 8. Rate Limiting
```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls=20, time_window=60):
        self.calls = deque()
        self.max_calls = max_calls
        self.time_window = time_window
    
    def can_call(self):
        now = time.time()
        # Remove old calls
        while self.calls and self.calls[0] < now - self.time_window:
            self.calls.popleft()
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
```

## Best Practices:

1. **Use VPS/Cloud Server** instead of local machine
2. **Set up monitoring** (Uptime Robot, Pingdom)
3. **Use systemd service** for auto-restart
4. **Implement graceful shutdown**
5. **Regular health checks**
6. **Database connection pooling**
7. **Async operations** for better performance

## Quick Fixes:

- Increase server RAM
- Use screen/tmux sessions
- Add exception handling everywhere
- Implement retry logic
- Use webhooks instead of polling
- Regular bot restarts (cron job)