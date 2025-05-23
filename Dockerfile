# Use an official Python image
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the start command
CMD ["python", "bot.py"]
