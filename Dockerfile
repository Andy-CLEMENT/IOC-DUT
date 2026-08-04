FROM ultralytics/ultralytics:latest-jetson-jetpack6

WORKDIR /app

# Dependencies
RUN apt-get update && apt-get install -y \
    psmisc \
    sudo \
    dos2unix \
    libgtk2.0-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# For web communication
RUN pip install --no-cache-dir websocket-client websockets

# Headless running
RUN pip uninstall -y opencv-python opencv-python-headless || true

COPY ./Fire-Detection-IA/Script-IA /app/Script-IA

# Use the IA compile file
COPY ./Fire-Detection-IA/Script-IA/fire-detect-model.engine /app/Script-IA/fire-detect-model.engine

RUN dos2unix /app/Script-IA/run.sh && chmod +x /app/Script-IA/run.sh

CMD ["/bin/bash", "/app/Script-IA/run.sh"]