# Use a lightweight Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install OS-level dependencies:
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and .env
COPY ingest_git.py .env ./

# Default command (can override via docker run)
CMD ["python", "ingest_git.py"]
