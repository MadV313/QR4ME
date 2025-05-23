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

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create runtime directories in case they're gitignored
RUN mkdir -p outputs previews data public/gallery

# Default command to run the bot
CMD ["python", "bot.py"]
