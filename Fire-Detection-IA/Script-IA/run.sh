#!/bin/bash

#faut faire chmod +x run.sh avant de executer

cd "$(dirname "$0")"

echo "--- Démarrage du système ---"

echo "Configuration du Wi-Fi..."
sudo iw dev wlan0 set power_save off

echo "Libération du port 8765..."
sudo fuser -k 8765/tcp > /dev/null 2>&1

echo "Lancement du serveur relais en arrière-plan..."
python3 serveur_relais.py > log_serveur.txt 2>&1 &
SERVEUR_PID=$!

sleep 2

echo "Lancement de l'IA (fire-detect.py)..."
echo "Appuyez sur 'q' dans la fenêtre vidéo pour quitter."
python3 fire-detect.py

echo "Arrêt en cours..."
kill $SERVEUR_PID > /dev/null 2>&1
sudo fuser -k 8765/tcp > /dev/null 2>&1

echo "Système arrêté proprement."