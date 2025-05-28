# Use a lightweight Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install OS‐level dependencies:
#  • libmagic for file‐type detection
#  • poppler-utils for pdftotext
#  • libGL + glib for OpenCV (cv2) so inference-based PDF parsing loads
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libmagic1 libmagic-dev \
      poppler-utils \
      libgl1-mesa-glx \
      libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir \
      -r requirements.txt \
      python-magic \
      "unstructured[pdf]"

# Copy your code + env
COPY ingest.py watcher.py .env ./

# Run the watcher
CMD ["python", "watcher.py"]
