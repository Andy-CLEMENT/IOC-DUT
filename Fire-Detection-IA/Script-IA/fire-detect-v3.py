import cv2
from ultralytics import YOLO
import threading
import queue
import time
import json
import sys
from datetime import datetime

try:
    import websocket
except ImportError:
    websocket = None

#Global configuration

# Video Stream settings
WS_URL = "ws://127.0.0.1:8765"  #  Put "ws://192.168.4.1/ws" for the real test
CAMERA_IP = "192.168.0.123"
USER = "admin"
PASSWORD = "123456"
GSTREAMER_PORT = 554
GSTREAMER_CHANNEL = 101
WINDOW_NAME = "Système de Détection Incendie IA - 4MP"

# AI Settings
MODEL_PATH = "model_020626.engine"
CONFIDENCE_PREDICT = 0.4
CONFIDENCE_DETECT = 0.6
SMOKE_LOW = 100
SMOKE_MEDIUM = 150
SMOKE_HEAVY = 650

# Code Behavior
COOLDOWN_SECONDS = 3.0   # Cooldown between 2 alerts
RECONNECT_DELAY = 5.0    # Cooldown before try another connection with the serveur
SEND_DELAY = 3.0         # Frenquency of data sending


# --- WebSocket
class WebSocketAlertSender:
    def __init__(self, url, queue_max=1000, reconnect_delay=RECONNECT_DELAY):
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


# --- GStreamer Functions ---
def gstreamer_pipeline_h264(user, password, ip, port=GSTREAMER_PORT, channel=GSTREAMER_CHANNEL):
    return (
        f"rtspsrc location=rtsp://{ip}:{port}/Streaming/Channels/{channel} "
        f"protocols=tcp user-id={user} user-pw={password} latency=200 ! "
        "rtph264depay ! h264parse ! "
        "nvv4l2decoder ! "
        "nvvidconv ! video/x-raw, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! "
        "appsink drop=true sync=false"
    )

def gstreamer_pipeline_h265(user, password, ip, port=GSTREAMER_PORT, channel=GSTREAMER_CHANNEL):
    return (
        f"rtspsrc location=rtsp://{ip}:{port}/Streaming/Channels/{channel} "
        f"protocols=tcp user-id={user} user-pw={password} latency=200 ! "
        "rtph265depay ! h265parse ! "
        "nvv4l2decoder ! "
        "nvvidconv ! video/x-raw, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! "
        "appsink drop=true sync=false"
    )

def connect_camera():
    print("Attempt connection with H.264...")
    cap = cv2.VideoCapture(gstreamer_pipeline_h264(USER, PASSWORD, CAMERA_IP), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        return cap
        
    print("H.264 do not work, try H.265...")
    cap = cv2.VideoCapture(gstreamer_pipeline_h265(USER, PASSWORD, CAMERA_IP), cv2.CAP_GSTREAMER)
    if cap.isOpened():
        return cap
        
    return None

# --- System initialisation ---
print(f"Loading ({MODEL_PATH}) on  GPU...")
model = None

try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Load of IA meet an issue: {e}")
    sys.exit(1)

# Check the model
if model is not None:
    print("IA ready !")

# WebSocket run
ws_sender = WebSocketAlertSender(WS_URL)
last_alert_time = 0.0  
program_running = True

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)

print("press 'q' to exit the program")

# Loop of work
while program_running:
    
    # Attempt to connect the camera
    cap = connect_camera()
    
    if cap is None or not cap.isOpened():
        print("Error : connection to the camera impossible, new attempt in few second...")
        ws_sender.send({
            "Camera": "Camera_Anpviz_1",
            "online": False,
            "error": "Impossible d'ouvrir le flux vidéo",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        time.sleep(RECONNECT_DELAY)
        continue  # new tentative

    print("✅ Connexion enable")
    ws_sender.send({
        "Camera": "Camera_Anpviz_1",
        "online": True,
        "message": "Flux vidéo restauré",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

    # Loop for IA processing
    while program_running:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ video stream lost !")
            ws_sender.send({
                "Camera": "Camera_Anpviz_1",
                "online": False,
                "error": "vido lost",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            cap.release()
            time.sleep(RECONNECT_DELAY)
            break
        #Ping signal to stay awake (every 2 sec)
        current_time = time.time()
        if (current_time - last_alert_time) > SEND_DELAY:
            ws_sender.send({
                "Camera": "Camera_Anpviz_1",
                "flame": False,
                "smoke": 100,
                "online": True,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            last_alert_time = current_time
            
        results = model.predict(source=frame, conf=CONFIDENCE_PREDICT, verbose=False)

        for box in results[0].boxes:
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            label = model.names[class_id]
            
            current_time = time.time()
            if confidence > CONFIDENCE_DETECT and (current_time - last_alert_time) > COOLDOWN_SECONDS:
                alerte = {
                    "Camera": "Camera_Anpviz_1",
                    "state": label,
                    "confiance": round(confidence * 100, 2)
                }
                print(f"🔥 ALERTE DÉCLENCHÉE : {alerte}")
                
                try:
                    payload = dict(alerte)
                    payload["online"] = True
                    payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
                    
                    if label.lower() == "fire":
                        payload["flame"] = True
                        payload["smoke"] = SMOKE_LOW  # Low Smoke
                    elif label.lower() == "smoke":
                        payload["flame"] = False
                        payload["smoke"] = SMOKE_HEAVY  # Heavy smoke
                    ok = ws_sender.send(payload)
                    if not ok:
                        print("⚠️ Send to ws is not working")
                    else:
                        last_alert_time = current_time 
                except Exception as e:
                    print(f"ERROR: {e}")
        
        annotated_frame = results[0].plot()
        cv2.imshow(WINDOW_NAME, annotated_frame)
        
        # Gestion de la fermeture propre du programme
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("'q' pressed, program is stopping.")
            program_running = False
            break
            
        try:
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_AUTOSIZE) == -1:
                print("Windows close with (X).")
                program_running = False
                break
        except cv2.error:
            program_running = False
            break

# --- Nettoyage final avant de quitter ---
if 'cap' in locals() and cap is not None:
    cap.release()
cv2.destroyAllWindows()
try:
    ws_sender.close()
except Exception:
    pass
print("Programme stopped")
