# Use a lightweight Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install the native libmagic and dev headers, then the Python binding
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libmagic1 libmagic-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install your Python deps plus the python-magic binding
RUN pip install --no-cache-dir -r requirements.txt python-magic

# Copy service code and .env
COPY ingest.py watcher.py .env ./

# Expose nothing (watcher runs in foreground)
# Entrypoint: start the watcher
CMD ["python", "watcher.py"]
