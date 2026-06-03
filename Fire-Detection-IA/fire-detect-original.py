import cv2
from ultralytics import YOLO

# 1. CHARGEMENT DU MODÈLE OPTIMISÉ TENSORRT
MODEL_PATH = "model_020626.engine"
print(f"Chargement du modèle TensorRT ({MODEL_PATH}) sur le GPU...")
model = YOLO(MODEL_PATH)
print("IA prête et optimisée !")

# 2. DEFINITIONS DES PIPELINES GSTREAMER
def gstreamer_pipeline_h264(user, password, ip, port=554, channel=101):
    return (
        f"rtspsrc location=rtsp://{ip}:{port}/Streaming/Channels/{channel} "
        f"protocols=tcp user-id={user} user-pw={password} latency=200 ! "
        "rtph264depay ! h264parse ! "
        "nvv4l2decoder ! "
        "nvvidconv ! video/x-raw, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! "
        "appsink drop=true sync=false"
    )

def gstreamer_pipeline_h265(user, password, ip, port=554, channel=101):
    return (
        f"rtspsrc location=rtsp://{ip}:{port}/Streaming/Channels/{channel} "
        f"protocols=tcp user-id={user} user-pw={password} latency=200 ! "
        "rtph265depay ! h265parse ! "
        "nvv4l2decoder ! "
        "nvvidconv ! video/x-raw, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! "
        "appsink drop=true sync=false"
    )

# Configuration de la caméra et de la fenêtre
WINDOW_NAME = "Système de Détection Incendie IA - 4MP"
CAMERA_IP = "192.168.0.123"
USER = "admin"
PASSWORD = "123456"

# Initialisation du flux vidéo avec tentative H.264
print("Tentative de connexion au flux H.264...")
RTSP_PIPELINE = gstreamer_pipeline_h264(USER, PASSWORD, CAMERA_IP)
cap = cv2.VideoCapture(RTSP_PIPELINE, cv2.CAP_GSTREAMER)

# Si le H.264 échoue, on bascule automatiquement sur le H.265 (comme dans lecteur_camera.py)
if not cap.isOpened():
    print("Échec du flux H.264. Tentative de bascule automatique en H.265...")
    RTSP_PIPELINE = gstreamer_pipeline_h265(USER, PASSWORD, CAMERA_IP)
    cap = cv2.VideoCapture(RTSP_PIPELINE, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir le flux vidéo de la caméra (H.264 et H.265 rejetés).")
    exit()

# Création de la fenêtre graphique
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)

print("\nAnalyse vidéo et prédictions IA en cours...")
print("Appuyez sur 'q' ou fermez la fenêtre (X) pour quitter.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Perte du flux vidéo ou erreur de lecture.")
        break
        
    # 3. PRÉDICTION IA ULTRA-RAPIDE (Inférence TensorRT sur le GPU)
    results = model.predict(source=frame, conf=0.4, verbose=False)
    
    # 4. RÉCUPÉRATION DE L'IMAGE ANNOTÉE PAR L'IA
    annotated_frame = results[0].plot()
    
    # 5. AFFICHAGE DU RÉSULTAT
    cv2.imshow(WINDOW_NAME, annotated_frame)
    
    # 6. GESTION DE LA FERMETURE ET DES TOUCHES
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Arrêt demandé via la touche 'q'.")
        break
        
    # Détection de la croix (X) pour éviter la réouverture de la fenêtre
    try:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_AUTOSIZE) == -1:
            print("Fenêtre fermée avec la croix (X).")
            break
    except cv2.error:
        break

# Libération propre des ressources
cap.release()
cv2.destroyAllWindows()
print("Système arrêté proprement.")
