# Utilisation de l'image de base Ultralytics optimisée pour processeurs ARM64 (Jetson)
FROM ultralytics/ultralytics:latest-arm64

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Installation des dépendances système nécessaires pour les commandes de run.sh
RUN apt-get update && apt-get install -y \
    psmisc \
    sudo \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Installation des bibliothèques Python supplémentaires (pour serveur_relais.py)
RUN pip install websockets

# Copie des scripts d'inférence
COPY ./Fire-Detection-IA/Script-IA /app/Script-IA

# Copie du modèle IA final (ajuste le nom si ton Python pointe vers un autre fichier)
COPY ./Fire-Detection-IA/model_final/best.pt /app/model_final/best.pt
COPY ./Fire-Detection-IA/yolo11m.pt /app/yolo11m.pt

# Attribution des droits d'exécution au script
RUN chmod +x /app/Script-IA/run.sh

# Commande par défaut au lancement du conteneur
CMD ["/app/Script-IA/run.sh"]