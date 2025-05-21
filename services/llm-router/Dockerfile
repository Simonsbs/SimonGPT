# Stage 1: builder
FROM python:3.12-slim AS builder
WORKDIR /app

# Install build deps
RUN apt-get update && \
    apt-get install -y build-essential gcc

# Copy and install only requirements
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: final image
FROM python:3.12-slim
WORKDIR /app

# Copy installed packages and app code
COPY --from=builder /install /usr/local
COPY app ./app
COPY .env .env

# Expose port and run
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
