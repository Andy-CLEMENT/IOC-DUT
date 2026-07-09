#!/usr/bin/env python3
# -----------------------------------------------------------------------
# fire_detect.py
#
# Detection de feu/fumee par IA (YOLO) sur flux camera RTSP.
# Alertes envoyees en temps reel a un serveur WebSocket.
#
# Style : procedural, structures explicites (struct) + fonctions.
# Chaque fonction module_action(struct, ...) prend sa structure en
# premier argument, comme un pointeur passe explicitement en C.
# -----------------------------------------------------------------------

import sys
import time
import json
import queue
import threading
from datetime import datetime, timezone

import cv2
from ultralytics import YOLO

try:
    import websocket
except ImportError:
    websocket = None


# ============================ CONSTANTES ==================================

CAMERA_IP               = "192.168.0.123"
CAMERA_USER             = "admin"
CAMERA_PASSWORD         = "123456"
CAMERA_NAME             = "Camera_Anpviz_1"
RTSP_PORT               = 554
RTSP_CHANNEL            = 101

WS_URL                  = "ws://127.0.0.1:8765"   # "ws://192.168.4.1/ws" pour test reel
WS_QUEUE_MAX            = 1000
WS_RECONNECT_DELAY_SEC  = 5.0

MODEL_PATH              = "fire-detect-model.engine"
CONFIDENCE_THRESHOLD    = 0.5
AI_INTERVAL_SEC         = 0.12   # ~8 images/seconde analysees

SMOKE_LOW               = 100
SMOKE_MEDIUM            = 150
SMOKE_HEAVY             = 650

ALERT_COOLDOWN_SEC      = 2.0
HEARTBEAT_INTERVAL_SEC  = 4.0

WINDOW_NAME             = "IA Fire Detection System - 4MP"
WINDOW_WIDTH            = 1280
WINDOW_HEIGHT           = 720


# ============================ STRUCTURES ===================================
# Champs uniquement, comme des struct en C. Toute la logique vit dans des
# fonctions separees qui recoivent la structure en premier argument.

class WsSender:
    __slots__ = ("url", "reconnect_delay", "msg_queue", "stop_event", "thread")


class Camera:
    __slots__ = ("cap",)


class Detector:
    __slots__ = ("model",)


class AppState:
    __slots__ = (
        "running",
        "last_heartbeat_time",
        "last_alert_time",
        "last_ai_time",
        "annotated_frame",
    )


# ============================ UTILITAIRES ==================================

def now_iso():
    """Horodatage UTC ISO 8601 (equivalent de l'ancien datetime.utcnow())."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def log_info(fmt, *args):
    print("[INFO ] " + (fmt % args if args else fmt))


def log_warn(fmt, *args):
    print("[WARN ] " + (fmt % args if args else fmt))


def log_error(fmt, *args):
    print("[ERROR] " + (fmt % args if args else fmt))


# ============================ MODULE WEBSOCKET ==============================
# ws_sender_* : equivalent d'un fichier .c/.h. Toutes les fonctions prennent
# une struct WsSender en premier argument.

def ws_sender_create(url, queue_max, reconnect_delay):
    ws = WsSender()
    ws.url = url
    ws.reconnect_delay = reconnect_delay
    ws.msg_queue = queue.Queue(maxsize=queue_max)
    ws.stop_event = threading.Event()
    ws.thread = threading.Thread(target=ws_sender_thread_main, args=(ws,), daemon=True)
    ws.thread.start()
    return ws


def ws_sender_send(ws, payload):
    """Empile un message JSON. Non bloquant. Retourne 1 si ok, 0 sinon."""
    if websocket is None:
        return 0
    try:
        ws.msg_queue.put_nowait(json.dumps(payload))
        return 1
    except queue.Full:
        log_warn("File WebSocket pleine, message perdu")
        return 0


def ws_sender_close(ws, timeout=2.0):
    ws.stop_event.set()
    ws.thread.join(timeout)


def ws_sender_thread_main(ws):
    if websocket is None:
        log_error("Module 'websocket' absent : alertes desactivees")
        return

    while not ws.stop_event.is_set():
        conn = None
        try:
            conn = websocket.create_connection(ws.url, timeout=8)
            ws_sender_pump(ws, conn)
        except Exception as exc:
            log_warn("Connexion WebSocket echouee (%s), retry dans %.1fs", exc, ws.reconnect_delay)
            time.sleep(ws.reconnect_delay)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass


def ws_sender_pump(ws, conn):
    """Boucle d'envoi tant que la connexion est valide. Retourne pour forcer un retry."""
    while not ws.stop_event.is_set():
        try:
            msg = ws.msg_queue.get(timeout=0.5)
        except queue.Empty:
            continue
        try:
            conn.send(msg)
        except Exception:
            ws_sender_requeue(ws, msg)
            return


def ws_sender_requeue(ws, msg):
    try:
        ws.msg_queue.put_nowait(msg)
    except queue.Full:
        pass


# ============================ MODULE CAMERA ==================================

def camera_build_pipeline(codec_id):
    """codec_id = 'h264' ou 'h265'."""
    if codec_id == "h264":
        depay = "rtph264depay ! h264parse"
    else:
        depay = "rtph265depay ! h265parse"

    url = "rtsp://%s:%d/Streaming/Channels/%d" % (CAMERA_IP, RTSP_PORT, RTSP_CHANNEL)

    return (
        "rtspsrc location=%s protocols=tcp user-id=%s user-pw=%s latency=200 ! "
        "%s ! nvv4l2decoder ! "
        "nvvidconv ! video/x-raw, format=(string)BGRx ! "
        "videoconvert ! video/x-raw, format=(string)BGR ! "
        "appsink drop=true sync=false"
    ) % (url, CAMERA_USER, CAMERA_PASSWORD, depay)


def camera_connect(cam):
    """Essaie H.264 puis H.265. Retourne 1 si succes, 0 sinon."""
    codecs = (("H.264", "h264"), ("H.265", "h265"))
    for codec_name, codec_id in codecs:
        log_info("Tentative de connexion camera en %s...", codec_name)
        pipeline = camera_build_pipeline(codec_id)
        cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
        if cap.isOpened():
            cam.cap = cap
            log_info("Connexion camera etablie (%s)", codec_name)
            return 1
    cam.cap = None
    return 0


def camera_read(cam):
    """Retourne (ok, frame) avec ok = 0/1."""
    if cam.cap is None:
        return 0, None
    ok, frame = cam.cap.read()
    return (1 if ok else 0), frame


def camera_release(cam):
    if cam.cap is not None:
        cam.cap.release()
        cam.cap = None


# ============================ MODULE DETECTEUR IA ============================

def detector_create(model_path):
    det = Detector()
    log_info("Chargement du modele IA (%s) sur GPU...", model_path)
    try:
        det.model = YOLO(model_path)
    except Exception as exc:
        log_error("Echec du chargement du modele IA : %s", exc)
        sys.exit(1)
    log_info("Modele IA pret.")
    return det


def detector_analyze(det, frame):
    """Retourne (frame_annotee, detections). detections = liste de (label, confiance)."""
    result = det.model.predict(source=frame, conf=CONFIDENCE_THRESHOLD, verbose=False)[0]
    annotated = result.plot()

    detections = []
    for box in result.boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        label = det.model.names[class_id]
        detections.append((label, confidence))

    return annotated, detections


def detector_build_alert_payload(camera_name, label, confidence):
    payload = {
        "Camera": camera_name,
        "state": label,
        "confiance": round(confidence * 100, 2),
        "online": True,
        "timestamp": now_iso(),
    }
    label_lc = label.lower()
    if label_lc == "fire":
        payload["flame"] = True
        payload["smoke"] = SMOKE_LOW
    elif label_lc == "smoke":
        payload["flame"] = False
        payload["smoke"] = SMOKE_HEAVY
    return payload


# ============================ ALERTES / HEARTBEAT ============================

def notify_online(ws, message):
    ws_sender_send(ws, {
        "Camera": CAMERA_NAME,
        "online": True,
        "message": message,
        "timestamp": now_iso(),
    })


def notify_offline(ws, error):
    ws_sender_send(ws, {
        "Camera": CAMERA_NAME,
        "online": False,
        "error": error,
        "timestamp": now_iso(),
    })


def send_heartbeat_if_due(ws, state):
    now = time.time()
    if (now - state.last_heartbeat_time) <= HEARTBEAT_INTERVAL_SEC:
        return
    ws_sender_send(ws, {
        "Camera": CAMERA_NAME,
        "flame": False,
        "smoke": 100,
        "online": True,
        "timestamp": now_iso(),
    })
    state.last_heartbeat_time = now


def handle_detections(ws, state, detections):
    """Envoie une alerte si une detection franchit le seuil, hors cooldown."""
    now = time.time()
    if (now - state.last_alert_time) <= ALERT_COOLDOWN_SEC:
        return

    for label, confidence in detections:
        if confidence <= CONFIDENCE_THRESHOLD:
            continue

        payload = detector_build_alert_payload(CAMERA_NAME, label, confidence)
        log_info("ALERTE : %s", payload)

        if ws_sender_send(ws, payload):
            state.last_alert_time = now
        else:
            log_warn("Echec de l'envoi de l'alerte au serveur WebSocket.")
        break  # une alerte par cycle suffit


# ============================ AFFICHAGE / ENTREES =============================

def should_quit():
    """Retourne 1 si l'utilisateur veut quitter (touche 'q' ou fenetre fermee)."""
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        log_info("Touche 'q' pressee, arret du programme.")
        return 1
    try:
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_AUTOSIZE) == -1:
            log_info("Fenetre fermee par l'utilisateur.")
            return 1
    except cv2.error:
        return 1
    return 0


# ============================ BOUCLE PRINCIPALE ================================

def stream_loop(ws, cam, det, state):
    """
    Boucle de lecture/analyse/affichage tant que le flux camera est valide.
    Retourne quand le flux est perdu ou que l'utilisateur quitte.
    """
    state.annotated_frame = None

    while state.running:
        ok, frame = camera_read(cam)
        if not ok:
            log_warn("Flux video perdu.")
            notify_offline(ws, "video lost")
            camera_release(cam)
            time.sleep(WS_RECONNECT_DELAY_SEC)
            return

        send_heartbeat_if_due(ws, state)

        now = time.time()
        if (now - state.last_ai_time) >= AI_INTERVAL_SEC:
            annotated, detections = detector_analyze(det, frame)
            state.annotated_frame = annotated
            state.last_ai_time = now
            handle_detections(ws, state, detections)

        if state.annotated_frame is not None:
            cv2.imshow(WINDOW_NAME, state.annotated_frame)
        else:
            cv2.imshow(WINDOW_NAME, frame)

        if should_quit():
            state.running = 0
            return


def main():
    det = detector_create(MODEL_PATH)
    ws = ws_sender_create(WS_URL, WS_QUEUE_MAX, WS_RECONNECT_DELAY_SEC)

    cam = Camera()
    cam.cap = None

    state = AppState()
    state.running = 1
    state.last_heartbeat_time = 0.0
    state.last_alert_time = 0.0
    state.last_ai_time = 0.0
    state.annotated_frame = None

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, WINDOW_WIDTH, WINDOW_HEIGHT)

    log_info("Appuyez sur 'q' pour quitter le programme.")

    while state.running:
        if not camera_connect(cam):
            notify_offline(ws, "Video Stream can't be read")
            time.sleep(WS_RECONNECT_DELAY_SEC)
            continue

        notify_online(ws, "Video Stream enabled")
        stream_loop(ws, cam, det, state)

    camera_release(cam)
    cv2.destroyAllWindows()
    ws_sender_close(ws)
    log_info("Programme arrete.")


if __name__ == "__main__":
    main()