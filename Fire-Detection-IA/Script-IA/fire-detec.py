import cv2
from ultralytics import YOLO
#ajout alexis pour communication websocket non bloquante
import threading
import queue
import time
import json
from datetime import datetime

try:
    import websocket
except Exception:
    websocket = None
# fin ajout alexis pour communication websocket non bloquante

# 1. CHARGEMENT DU MODÈLE OPTIMISÉ TENSORRT
MODEL_PATH = "model_020626.engine"
print(f"Chargement du modèle TensorRT ({MODEL_PATH}) sur le GPU...")
model = YOLO(MODEL_PATH)
print("IA prête et optimisée !")

# ajout alexis pour communication websocket non bloquante --- WebSocket non-bloquant pour envoyer les alertes au dashboard ---
class WebSocketAlertSender:
    def __init__(self, url, queue_max=1000, reconnect_delay=5):
        self.url = url
        self.queue = queue.Queue(maxsize=queue_max)
        self.reconnect_delay = reconnect_delay
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def send(self, payload: dict) -> bool:
        """Queue le payload (dict). Ne bloque pas l'émetteur vidéo.
        Retourne False si la queue est pleine ou si websocket-client n'est pas disponible.
        """
        if websocket is None:
            return False
        try:
            self.queue.put_nowait(json.dumps(payload))
            return True
        except queue.Full:
            return False

    def _run(self):
        if websocket is None:
            # bibliothèque absente, on ne tente rien
            return

        while not self._stop.is_set():
            ws = None
            try:
                ws = websocket.create_connection(self.url, timeout=8)
                while not self._stop.is_set():
                    try:
                        msg = self.queue.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    try:
                        ws.send(msg)
                    except Exception:
                        # échec d'envoi -> remettre le message si possible et reconnecter
                        try:
                            self.queue.put_nowait(msg)
                        except queue.Full:
                            pass
                        break
            except Exception:
                time.sleep(self.reconnect_delay)
            finally:
                try:
                    if ws:
                        ws.close()
                except Exception:
                    pass

    def close(self, timeout=2.0):
        self._stop.set()
        self._thread.join(timeout)

# URL du dashboard (valeur par défaut vue dans le frontend)
WS_URL = "ws://192.168.4.1/ws"
ws_sender = WebSocketAlertSender(WS_URL)

#fin ajout alexis pour communication websocket non bloquante

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

    # On vérifie chaque objet détecté par l'IA dans l'image
    for box in results[0].boxes:
        # On récupère le niveau de confiance et le type (0 ou 1)
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])
        label = model.names[class_id] # 'fire' ou 'smoke'
        
        # Si l'IA est sûre à plus de 60 %
        if confidence > 0.60:
            # On crée un message d'alerte structuré
            alerte = {
                "capteur": "Camera_Anpviz_1",
                "type_alerte": label,
                "confiance": round(confidence * 100, 2)
            }
            print(f"!! ALERTE DÉCLENCHÉE : {alerte}")
            #ajout alexis pour communication websocket non bloquante
            # Envoi non-bloquant vers le dashboard via WebSocket
            try:
                # enrichit le message avec un timestamp pour le dashboard
                payload = dict(alerte)
                payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
                # expose un champ `flame` attendu par le dashboard (true si type_alerte == 'fire')
                payload["flame"] = True if label.lower() == "fire" else False

                ok = ws_sender.send(payload)
                if not ok:
                    # échec d'enqueue (queue pleine ou websocket non disponible)
                    print("Envoi WS non effectué (queue pleine ou lib manquante)")
            except Exception as e:
                print(f"Erreur en préparant l'alerte réseau: {e}")
                #fin ajout alexis pour communication websocket non bloquante
    
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
# Ferme proprement le thread d'envoi WS
try:
    ws_sender.close()
except Exception:
    pass
print("Système arrêté proprement.")
