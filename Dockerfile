FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling psycopg2 if required
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ /app/backend/

# Set working directory to backend for uvicorn
WORKDIR /app/backend

# Hugging Face Spaces uses port 7860 by default
EXPOSE 7860

# Command to run uvicorn on port 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
