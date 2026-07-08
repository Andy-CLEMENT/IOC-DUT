"""
fire_detect.py

Systeme de detection de feu et fumee par IA (YOLO) sur flux camera RTSP,
avec envoi d'alertes en temps reel vers un dashboard via WebSocket.

Architecture :
    Config           - toute la configuration au meme endroit
    CameraStream     - connexion et lecture du flux camera (GStreamer/RTSP)
    AlertSender      - envoi asynchrone des messages vers le serveur WebSocket
    FireDetector     - encapsule le modele YOLO et l'interpretation des resultats
    FireDetectionApp - orchestre les composants ci-dessus (boucle principale)
"""

import sys
import time
import json
import queue
import logging
import threading
from dataclasses import dataclass
from datetime import datetime, timezone

import cv2
from ultralytics import YOLO

try:
    import websocket
except ImportError:
    websocket = None


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

@dataclass(frozen=True)
class Config:
    # Connexion camera
    camera_ip: str = "192.168.0.123"
    camera_user: str = "admin"
    camera_password: str = "123456"
    camera_name: str = "Camera_Anpviz_1"
    rtsp_port: int = 554
    rtsp_channel: int = 101

    # WebSocket
    ws_url: str = "ws://127.0.0.1:8765"  # "ws://192.168.4.1/ws" pour le test reel
    ws_queue_max: int = 1000
    ws_reconnect_delay: float = 5.0

    # Modele IA
    model_path: str = "fire-detect-model.engine"
    confidence_threshold: float = 0.5
    ai_interval_seconds: float = 0.12  # ~8 images/seconde analysees

    # Niveaux de fumee envoyes au dashboard
    smoke_low: int = 100
    smoke_medium: int = 150
    smoke_heavy: int = 650

    # Comportement des alertes
    alert_cooldown_seconds: float = 2.0      # delai minimum entre deux alertes
    heartbeat_interval_seconds: float = 4.0  # signal "je suis vivant" regulier

    # Affichage
    window_name: str = "IA Fire Detection System - 4MP"
    window_width: int = 1280
    window_height: int = 720


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fire-detect")


def now_iso() -> str:
    """Horodatage UTC au format ISO 8601 (equivalent a l'ancien datetime.utcnow())."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ----------------------------------------------------------------------
# WebSocket : envoi des alertes en arriere-plan
# ----------------------------------------------------------------------

class AlertSender:
    """
    Envoie des messages JSON vers un serveur WebSocket dans un thread dedie.
    Se reconnecte automatiquement en cas de coupure, sans jamais bloquer
    l'appelant (send() est non-bloquant).
    """

    def __init__(self, url: str, queue_max: int, reconnect_delay: float):
        self._url = url
        self._reconnect_delay = reconnect_delay
        self._queue: "queue.Queue[str]" = queue.Queue(maxsize=queue_max)
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def send(self, payload: dict) -> bool:
        """Ajoute un message a la file d'envoi. Retourne False si websocket est absent ou la file pleine."""
        if websocket is None:
            return False
        try:
            self._queue.put_nowait(json.dumps(payload))
            return True
        except queue.Full:
            log.warning("File d'attente WebSocket pleine, message perdu")
            return False

    def close(self, timeout: float = 2.0):
        self._stop_event.set()
        self._thread.join(timeout)

    def _run(self):
        if websocket is None:
            log.error("Module 'websocket' non installe : les alertes ne seront pas envoyees")
            return

        while not self._stop_event.is_set():
            try:
                self._connection_loop()
            except Exception as exc:
                log.warning(
                    "Connexion WebSocket echouee (%s), nouvelle tentative dans %.1fs",
                    exc, self._reconnect_delay,
                )
                time.sleep(self._reconnect_delay)

    def _connection_loop(self):
        ws = websocket.create_connection(self._url, timeout=8)
        try:
            while not self._stop_event.is_set():
                try:
                    message = self._queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                try:
                    ws.send(message)
                except Exception:
                    self._requeue(message)
                    raise  # force une reconnexion
        finally:
            ws.close()

    def _requeue(self, message: str):
        try:
            self._queue.put_nowait(message)
        except queue.Full:
            pass


# ----------------------------------------------------------------------
# Camera : connexion GStreamer/RTSP avec repli H.264 -> H.265
# ----------------------------------------------------------------------

class CameraStream:
    """Gere la connexion a la camera RTSP via GStreamer, avec repli H.265 si H.264 echoue."""

    def __init__(self, config: Config):
        self._cfg = config
        self._cap = None

    def connect(self) -> bool:
        """Tente une connexion H.264 puis H.265. Retourne True si succes."""
        for name, pipeline_fn in (("H.264", self._pipeline_h264), ("H.265", self._pipeline_h265)):
            log.info("Tentative de connexion camera en %s...", name)
            cap = cv2.VideoCapture(pipeline_fn(), cv2.CAP_GSTREAMER)
            if cap.isOpened():
                self._cap = cap
                log.info("Connexion camera etablie (%s)", name)
                return True
        self._cap = None
        return False

    def read(self):
        """Retourne (succes, frame). Ne leve jamais si la camera n'est pas connectee."""
        if self._cap is None:
            return False, None
        return self._cap.read()

    def release(self):
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def _rtsp_url(self) -> str:
        c = self._cfg
        return f"rtsp://{c.camera_ip}:{c.rtsp_port}/Streaming/Channels/{c.rtsp_channel}"

    def _pipeline_h264(self) -> str:
        return (
            f"rtspsrc location={self._rtsp_url()} protocols=tcp "
            f"user-id={self._cfg.camera_user} user-pw={self._cfg.camera_password} latency=200 ! "
            "rtph264depay ! h264parse ! nvv4l2decoder ! "
            "nvvidconv ! video/x-raw, format=(string)BGRx ! "
            "videoconvert ! video/x-raw, format=(string)BGR ! "
            "appsink drop=true sync=false"
        )

    def _pipeline_h265(self) -> str:
        return (
            f"rtspsrc location={self._rtsp_url()} protocols=tcp "
            f"user-id={self._cfg.camera_user} user-pw={self._cfg.camera_password} latency=200 ! "
            "rtph265depay ! h265parse ! nvv4l2decoder ! "
            "nvvidconv ! video/x-raw, format=(string)BGRx ! "
            "videoconvert ! video/x-raw, format=(string)BGR ! "
            "appsink drop=true sync=false"
        )


# ----------------------------------------------------------------------
# Detection IA : chargement du modele et interpretation des resultats
# ----------------------------------------------------------------------

class FireDetector:
    """Encapsule le modele YOLO et la construction des payloads d'alerte."""

    def __init__(self, config: Config):
        self._cfg = config
        log.info("Chargement du modele IA (%s) sur GPU...", config.model_path)
        try:
            self.model = YOLO(config.model_path)
        except Exception as exc:
            log.error("Echec du chargement du modele IA : %s", exc)
            sys.exit(1)
        log.info("Modele IA pret.")

    def analyze(self, frame):
        """
        Lance l'inference sur une frame.
        Retourne (frame_annotee, detections) ou detections est une liste
        de tuples (label, confiance).
        """
        results = self.model.predict(
            source=frame, conf=self._cfg.confidence_threshold, verbose=False
        )[0]
        annotated = results.plot()

        detections = [
            (self.model.names[int(box.cls[0])], float(box.conf[0]))
            for box in results.boxes
        ]
        return annotated, detections

    def build_alert_payload(self, camera_name: str, label: str, confidence: float) -> dict:
        payload = {
            "Camera": camera_name,
            "state": label,
            "confiance": round(confidence * 100, 2),
            "online": True,
            "timestamp": now_iso(),
        }
        if label.lower() == "fire":
            payload["flame"] = True
            payload["smoke"] = self._cfg.smoke_low
        elif label.lower() == "smoke":
            payload["flame"] = False
            payload["smoke"] = self._cfg.smoke_heavy
        return payload


# ----------------------------------------------------------------------
# Application principale
# ----------------------------------------------------------------------

class FireDetectionApp:
    def __init__(self, config: Config):
        self.cfg = config
        self.detector = FireDetector(config)
        self.alert_sender = AlertSender(config.ws_url, config.ws_queue_max, config.ws_reconnect_delay)
        self.camera = CameraStream(config)

        self._last_heartbeat = 0.0
        self._last_alert = 0.0
        self._last_ai_run = 0.0
        self._running = True

        cv2.namedWindow(config.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(config.window_name, config.window_width, config.window_height)

    def run(self):
        log.info("Appuyez sur 'q' pour quitter le programme.")
        try:
            while self._running:
                if not self.camera.connect():
                    self._notify_offline("Video Stream can't be read")
                    time.sleep(self.cfg.ws_reconnect_delay)
                    continue
                self._notify_online("Video Stream enabled")
                self._stream_loop()
        finally:
            self._shutdown()

    def _stream_loop(self):
        """Boucle de lecture/analyse/affichage tant que le flux camera est valide."""
        annotated_frame = None

        while self._running:
            ok, frame = self.camera.read()
            if not ok:
                log.warning("Flux video perdu.")
                self._notify_offline("video lost")
                self.camera.release()
                time.sleep(self.cfg.ws_reconnect_delay)
                return

            self._send_heartbeat_if_due()

            if self._ai_due():
                annotated_frame, detections = self.detector.analyze(frame)
                self._last_ai_run = time.time()
                self._handle_detections(detections)

            cv2.imshow(self.cfg.window_name, annotated_frame if annotated_frame is not None else frame)

            if self._should_quit():
                self._running = False
                return

    def _ai_due(self) -> bool:
        return (time.time() - self._last_ai_run) >= self.cfg.ai_interval_seconds

    def _send_heartbeat_if_due(self):
        """Signal 'online' regulier, independant du cooldown des alertes."""
        now = time.time()
        if (now - self._last_heartbeat) > self.cfg.heartbeat_interval_seconds:
            self.alert_sender.send({
                "Camera": self.cfg.camera_name,
                "flame": False,
                "smoke": 100,
                "online": True,
                "timestamp": now_iso(),
            })
            self._last_heartbeat = now

    def _handle_detections(self, detections):
        """Envoie une alerte si une detection franchit le seuil, en respectant le cooldown."""
        now = time.time()
        if (now - self._last_alert) <= self.cfg.alert_cooldown_seconds:
            return  # encore en cooldown, on ignore ce cycle

        for label, confidence in detections:
            if confidence <= self.cfg.confidence_threshold:
                continue

            payload = self.detector.build_alert_payload(self.cfg.camera_name, label, confidence)
            log.info("ALERTE : %s", payload)

            if self.alert_sender.send(payload):
                self._last_alert = now
            else:
                log.warning("Echec de l'envoi de l'alerte au serveur WebSocket.")
            break  # une alerte par cycle suffit

    def _should_quit(self) -> bool:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            log.info("Touche 'q' pressee, arret du programme.")
            return True
        try:
            if cv2.getWindowProperty(self.cfg.window_name, cv2.WND_PROP_AUTOSIZE) == -1:
                log.info("Fenetre fermee par l'utilisateur.")
                return True
        except cv2.error:
            return True
        return False

    def _notify_online(self, message: str):
        self.alert_sender.send({
            "Camera": self.cfg.camera_name,
            "online": True,
            "message": message,
            "timestamp": now_iso(),
        })

    def _notify_offline(self, error: str):
        self.alert_sender.send({
            "Camera": self.cfg.camera_name,
            "online": False,
            "error": error,
            "timestamp": now_iso(),
        })

    def _shutdown(self):
        self.camera.release()
        cv2.destroyAllWindows()
        self.alert_sender.close()
        log.info("Programme arrete.")


if __name__ == "__main__":
    app = FireDetectionApp(Config())
    app.run()