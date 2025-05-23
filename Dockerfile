# Use an official lightweight Python image
FROM python:3.12-slim

# Install system dependencies required by pyzbar, opencv, etc.
RUN apt-get update && apt-get install -y \
    libzbar0 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy all project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set default command to run your bot
CMD ["python", "bot.py"]
