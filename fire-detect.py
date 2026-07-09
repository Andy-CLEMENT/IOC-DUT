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

# Global configuration

# Video Stream settings
WS_URL = "ws://127.0.0.1:8765"  #  Put "ws://192.168.4.1/ws" for the real test
CAMERA_IP = "192.168.0.123"
CAMERA_NAME = "Camera_Anpviz_1"
USER = "admin"
PASSWORD = "123456"
GSTREAMER_PORT = 554
GSTREAMER_CHANNEL = 101
WINDOW_NAME = "IA Fire Detection System - 4MP"

# AI Settings
MODEL_PATH = "fire-detect-model.engine"
CONFIDENCE_PREDICT = 0.4   # To display boxes
CONFIDENCE_DETECT = 0.5    # To send an Alert
SMOKE_LOW = 100
SMOKE_MEDIUM = 150
SMOKE_HEAVY = 650

# Code Behavior
COOLDOWN_SECONDS = 2.0   # Delay between 2 alerts
RECONNECT_DELAY = 5.0    # Cooldown before another attempt to connect to the server
SEND_DELAY = 4.0         # Period of heartbeat

# Interval of IA computing (en secondes)
AI_INTERVAL_SECONDS = 0.12  # ~8 pictures/sec analysed


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


# --- Building JSON tram --------------------------------------

def build_status_payload(online: bool, message: str = None, error: str = None) -> dict:
    """Camera status packet (connection established / lost)."""
    payload = {
        "Camera": CAMERA_NAME,
        "online": online,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    if message is not None:
        payload["message"] = message
    if error is not None:
        payload["error"] = error
    return payload


def build_heartbeat_payload() -> dict:
    """A “ping” packet is sent periodically to indicate that the system is active."""
    return {
        "Camera": CAMERA_NAME,
        "flame": False,
        "smoke": 100,
        "online": True,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def build_alert_payload(label: str, confidence: float) -> dict:
    """Alert packet sent when fire or smoke is detected."""
    payload = {
        "Camera": CAMERA_NAME,
        "state": label,
        "confiance": round(confidence * 100, 2),
        "online": True,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    label_lower = label.lower()
    if label_lower == "fire":
        payload["flame"] = True
        payload["smoke"] = SMOKE_LOW
    elif label_lower == "smoke":
        payload["flame"] = False
        payload["smoke"] = SMOKE_HEAVY
    return payload


# --- System Initialization -------------------------------------------
print(f"Loading ({MODEL_PATH}) on GPU...")
try:
    model = YOLO(MODEL_PATH)
except Exception as e:
    print(f"Load of IA meet an issue: {e}")
    sys.exit(1)
print("IA ready !")

ws_sender = WebSocketAlertSender(WS_URL)

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)

print("press 'q' to exit the program")


# --- Boucle principale ----------------------------------------------------
program_running = True
last_heartbeat_time = 0.0   # Last “ping” sent (separate from alerts)
last_alert_time = 0.0       # Last fire/smoke alert sent (manages the cooldown)
last_ai_time = 0.0          # last AI inference run

while program_running:

    cap = connect_camera()
    if cap is None or not cap.isOpened():
        print("Error : connection to the camera impossible, new attempt in few second...")
        ws_sender.send(build_status_payload(online=False, error="Video Stream can't be read"))
        time.sleep(RECONNECT_DELAY)
        continue

    print("✅ Connexion enable")
    ws_sender.send(build_status_payload(online=True, message="Video Stream enabled"))

    annotated_frame = None

    while program_running:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ video stream lost !")
            ws_sender.send(build_status_payload(online=False, error="video lost"))
            cap.release()
            time.sleep(RECONNECT_DELAY)
            break

        now = time.time()

        # Regular heartbeat: completely independent of the alert cooldown
        if (now - last_heartbeat_time) > SEND_DELAY:
            ws_sender.send(build_heartbeat_payload())
            last_heartbeat_time = now

        # AI inference, timed by AI_INTERVAL_SECONDS
        if (now - last_ai_time) >= AI_INTERVAL_SECONDS:
            results = model.predict(source=frame, conf=CONFIDENCE_PREDICT, verbose=False)[0]
            annotated_frame = results.plot()
            last_ai_time = now

            # We only check for an alert if the cooldown has expired
            if (now - last_alert_time) > COOLDOWN_SECONDS:
                for box in results.boxes:
                    confidence = float(box.conf[0])
                    if confidence <= CONFIDENCE_DETECT:
                        continue  # below the alert threshold, ignored (but displayed)

                    label = model.names[int(box.cls[0])]
                    payload = build_alert_payload(label, confidence)
                    print(f"🔥 FIRE ALERTE : {payload}")

                    if ws_sender.send(payload):
                        last_alert_time = now
                    else:
                        print("⚠️ Send to ws is not working")
                    break  # Only one alert per cycle: respects the cooldown

        # Feed View
        cv2.imshow(WINDOW_NAME, annotated_frame if annotated_frame is not None else frame)

        # Handling the Proper Termination of the Program
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

# --- Final cleaning before leaving ---
if 'cap' in locals() and cap is not None:
    cap.release()
cv2.destroyAllWindows()
try:
    ws_sender.close()
except Exception:
    pass
print("Programme stopped")