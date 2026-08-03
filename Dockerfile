# Use the Ultralytics base image optimized for ARM64 processors (Jetson)
FROM ultralytics/ultralytics:latest-arm64

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for run.sh commands
RUN apt-get update && apt-get install -y \
    psmisc \
    sudo \
    libgl1 \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

RUN pip install websockets

COPY ./Fire-Detection-IA/Script-IA /app/Script-IA

# Copy the final AI model
COPY ./Fire-Detection-IA/model_final/best.pt /app/model_final/best.pt
COPY ./Fire-Detection-IA/yolo11m.pt /app/yolo11m.pt

# Grant execution permissions to the script
RUN dos2unix /app/Script-IA/run.sh && chmod +x /app/Script-IA/run.sh

# Default command when starting the container
CMD ["/bin/bash ", "/app/Script-IA/run.sh"]