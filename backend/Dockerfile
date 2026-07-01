FROM python:3.11-slim

WORKDIR /app

# Install system deps for psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create models directory
RUN mkdir -p /app/app/ml/models

# Expose the HF Spaces default port
EXPOSE 7860

# HF Spaces sets PORT=7860
CMD ["python", "app.py"]
