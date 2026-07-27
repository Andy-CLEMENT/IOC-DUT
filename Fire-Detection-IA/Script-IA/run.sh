#!/bin/bash

cd "$(dirname "$0")"

echo "--- System Startup ---"

echo "Wi-Fi Setup..."
sudo iw dev wlan0 set power_save off

echo "Port 8765 released..."
sudo fuser -k 8765/tcp > /dev/null 2>&1

echo "Launching the relay server in the background..."
python3 serveur_relais.py > log_serveur.txt 2>&1 &
SERVEUR_PID=$!

sleep 2

echo "Launching the AI (fire-detect.py)..."
echo "Press 'q' in the video window to exit"
python3 fire-detect.py

echo "Stopping now..."
kill $SERVEUR_PID > /dev/null 2>&1
sudo fuser -k 8765/tcp > /dev/null 2>&1

echo "The system shut down properly"