FROM python:3.11-slim

# Set metadata
LABEL maintainer="Sandy Sniper Bot"
LABEL description="Ultimate Sandy Sniper Bot v5.0 - Persistent Trading Analysis"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libta-lib0-dev \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY ultimate_sandy_sniper_bot.py .
COPY .env* ./

# Create directories and set permissions
RUN mkdir -p logs data && \
    useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

# Switch to non-root user
USER botuser

# Create health check endpoint
RUN echo '#!/usr/bin/env python3\n\
import http.server\n\
import socketserver\n\
import threading\n\
\n\
def health_server():\n\
    handler = http.server.SimpleHTTPRequestHandler\n\
    with socketserver.TCPServer(("", 8000), handler) as httpd:\n\
        httpd.serve_forever()\n\
\n\
if __name__ == "__main__":\n\
    threading.Thread(target=health_server, daemon=True).start()\n\
    exec(open("ultimate_sandy_sniper_bot.py").read())' > app_with_health.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Set timezone
ENV TZ=Asia/Kolkata

# Expose health check port
EXPOSE 8000

# Run bot with health check
CMD ["python3", "app_with_health.py"]
