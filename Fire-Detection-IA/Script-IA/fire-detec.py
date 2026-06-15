import cv2
from ultralytics import YOLO
import threading
import queue
import time
import json
from datetime import datetime

try:
    import websocket
except ImportError:
    websocket = None

# ==========================================
# CONFIGURATION GLOBALE (Ajuste tes valeurs ici)
# ==========================================
MODEL_PATH = "model_020626.engine"
WS_URL = "ws://127.0.0.1:8765"  # Ca c'est pour le test -> Remettre "ws://192.168.4.1/ws" pour le vrai serveur
CAMERA_IP = "192.168.0.123"
USER = "admin"
PASSWORD = "123456"
WINDOW_NAME = "Système de Détection Incendie IA - 4MP"

COOLDOWN_SECONDS = 3.0  # Temps d'attente entre deux envois d'alertes réseau
# ==========================================


# --- WebSocket non-bloquant pour envoyer les alertes au dashboard ---
class WebSocketAlertSender:
    def __init__(self, url, queue_max=1000, reconnect_delay=5):
        self.url = url
        self.queue = queue.Queue(maxsize=queue_max)
        self.reconnect_delay = reconnect_delay
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def send(self, payload: dict) -> bool:
        if websocket is None:
            return False
        try:
            self.queue.put_nowait(json.dumps(payload))
            return True
        except queue.Full:
            return False

    def _run(self):
        if websocket is None:
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


# --- Fonctions GStreamer ---
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

# --- Initialisation du Système ---
print(f"Chargement du modèle TensorRT ({MODEL_PATH}) sur le GPU...")
model = YOLO(MODEL_PATH)
print("IA prête et optimisée !")

ws_sender = WebSocketAlertSender(WS_URL)
last_alert_time = 0.0  # Initialisation du chronomètre d'alerte

print("Tentative de connexion au flux H.264...")
RTSP_PIPELINE = gstreamer_pipeline_h264(USER, PASSWORD, CAMERA_IP)
cap = cv2.VideoCapture(RTSP_PIPELINE, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Échec du flux H.264. Tentative de bascule automatique en H.265...")
    RTSP_PIPELINE = gstreamer_pipeline_h265(USER, PASSWORD, CAMERA_IP)
    cap = cv2.VideoCapture(RTSP_PIPELINE, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir le flux vidéo de la caméra.")
    exit()

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)

print("\nAnalyse vidéo et prédictions IA en cours...")
print("Appuyez sur 'q' ou fermez la fenêtre (X) pour quitter.")

# --- Boucle Principale ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("Perte du flux vidéo ou erreur de lecture.")
        break
        
    results = model.predict(source=frame, conf=0.4, verbose=False)

    for box in results[0].boxes:
        confidence = float(box.conf[0])
        class_id = int(box.cls[0])
        label = model.names[class_id]
        
        # Condition d'alerte : Confiance > 60% ET le temps de cooldown est écoulé
        current_time = time.time()
        if confidence > 0.60 and (current_time - last_alert_time) > COOLDOWN_SECONDS:
            alerte = {
                "capteur": "Camera_Anpviz_1",
                "type_alerte": label,
                "confiance": round(confidence * 100, 2)
            }
            print(f"🔥 ALERTE DÉCLENCHÉE : {alerte}")
            
            try:
                payload = dict(alerte)
                payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
                payload["flame"] = True if label.lower() == "fire" else False

                ok = ws_sender.send(payload)
                if not ok:
                    print("⚠️ Envoi WS non effectué (queue pleine ou lib manquante)")
                else:
                    # On met à jour le chronomètre seulement si le message est bien parti
                    last_alert_time = current_time 
            except Exception as e:
                print(f"Erreur en préparant l'alerte réseau: {e}")
    
    annotated_frame = results[0].plot()
    cv2.imshow(WINDOW_NAME, annotated_frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Arrêt demandé via la touche 'q'.")
        break
        
    try:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_AUTOSIZE) == -1:
            print("Fenêtre fermée avec la croix (X).")
            break
    except cv2.error:
        break

cap.release()
cv2.destroyAllWindows()
try:
    ws_sender.close()
except Exception:
    pass
print("Système arrêté proprement.")