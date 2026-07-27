cd "$(dirname "$0")"

echo "--- running the system ---"

echo "Wi-Fi configuration..."
sudo iw dev wlP1p1s0 set power_save off

echo "clean port 8765..."
sudo fuser -k 8765/tcp > /dev/null 2>&1

echo "running server..."
python3 serveur_relais.py > log_serveur.txt 2>&1 &
SERVEUR_PID=$!

sleep 2

echo "run IA (fire-detect.py)..."
echo "press 'q' to quit."
python3 fire-detect.py

echo "switch off..."
kill $SERVEUR_PID > /dev/null 2>&1
sudo fuser -k 8765/tcp > /dev/null 2>&1

echo "program stopped."
