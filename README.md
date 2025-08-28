FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "src.main:create_app()"]
# driveline-driver-profile-api
