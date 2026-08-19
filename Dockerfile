# Google Cloud Run Dockerfile
# Builds a lightweight container for the Flask accessibility agent.

FROM python:3.9-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if needed (e.g. for sqlite/pandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port (Cloud Run sets PORT env variable, usually 8080)
EXPOSE 8080

# Run using gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 wsgi:application
