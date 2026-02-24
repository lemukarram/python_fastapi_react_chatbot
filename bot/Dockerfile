# Using Python 3.11 slim
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for asyncpg and PostgreSQL drivers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from /bot folder
COPY requirements.txt .

# Install dependencies (Docker handles the "environment" isolation for you)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy everything from /bot into the container's /app folder
COPY . .

EXPOSE 8000

# Since your code is in /bot/app/main.py, the command must be app.main:app
# We use 0.0.0.0 to make it accessible outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]