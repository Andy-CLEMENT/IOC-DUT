# IOC-DUT — Repository Summary and Organization

This document serves as an entry point for navigating the [IOC-DUT](https://github.com/Andy-CLEMENT/IOC-DUT) repository, used as part of the internship at DNIIT (Da Nang) on the Intelligent Operation Center (IOC), carried out by Andy CLEMENT and Alexis MARTINI.

Internship planning: [Google Sheets](https://docs.google.com/spreadsheets/d/1JbVak5m1N3S0Dq-XeGyO9e7A00-PoN9cihRR5XMIRzQ/edit?gid=1161341563#gid=1161341563)

---

## Table of Contents

1. [Daily-Report](#1-daily-report) — daily reports
2. [Documents](#2-documents) — internship report and scientific papers
3. [Fire-Detection-IA](#3-fire-detection-ia) — fire/smoke detection AI model (the part Sadewa works on)
4. [Vietnamese-Code](#4-vietnamese-code) — legacy work from the Vietnamese team
5. [Root files](#5-root-files)
6. [System Deployment (Docker)](#6-system-deployment-docker)
7. [Quick Workflow Summary](#7-quick-workflow-summary)

---

## 1. Daily-Report

Daily reports written by each project member.

```
Daily-Report/
├── Alexis/
│   └── 020626.md
└── Andy/
    ├── report-06-03.md
    ├── report-06-15.md
    ├── report-06-17.md
    ├── report-06-23.md
    ├── report-06-31.md
    ├── report-07-10.md
    └── report-07-21.md
```

---

## 2. Documents

Official internship report and scientific bibliography used for the writing/research part.

```
Documents/
├── 30. DUT_Design and Development of an Intelligent Operation Center
│   (IOC) for Building Energy Management and Automated Control.pdf
└── Papers/          # 21 scientific papers (fire detection, deep
                      # learning, edge AI, building energy management...)
```

---

## 3. Fire-Detection-IA

Core of the camera-based fire and smoke detection project, deployed on the Jetson Orin Nano.

```
Fire-Detection-IA/
├── README.md                  # folder overview
├── To-Do.md                   # remaining tasks list
├── Overall_System_Design.png  # overall system diagram
├── yolo11m.pt                 # YOLO11m model weights
│
├── Data-Sheet/                # hardware datasheets (IP camera, Jetson Orin Nano)
│
├── Script-IA/                 # Python scripts running on the Jetson
│   ├── fire-detect.py         # main detection pipeline (GStreamer/RTSP → YOLO → WebSocket)
│   ├── serveur_relais.py      # relays data to the dashboard
│   ├── serveur_test.py        # server test script
│   └── run.sh                 # launches fire-detect.py and serveur_relais.py together (alias `fire-detect`)
│
├── training_model/            # training scripts for the different model versions
│   ├── trainV1.py … trainV4.py
│   └── train_resume.py
│
├── model_final/                # best model retained (best.pt)
│
├── predictions/                # prediction scripts and results on test images
│   ├── predict.py
│   └── test_after_training/
│
├── runs/detect/…                # raw Ultralytics training results
│   ├── yolov8s_fire_v1/         # YOLOv8s baseline (~84% accuracy)
│   ├── yolo11m_fire_v2/ … v4/   # YOLO11m model iterations
│       (PR/F1 curves, confusion matrices, best.pt/last.pt weights, etc.)
│
└── Test-screen/                # detection screenshots (fire/smoke)
```

> The `run.sh` script + the `fire-detect` alias (defined in `~/.bashrc` on the Jetson) let you launch the entire pipeline with a single command: `fire-detect`.

---

## 4. Vietnamese-Code

Previous work carried out by the Vietnamese team, reused and adapted for the internship.

```
Vietnamese-Code/
├── README.md
│
├── Alarm-System-Electronics/     # electronic alarm system (Arduino + PCB)
│   ├── Code/                     # .ino sketches (den_coi_final, nutnhan3, testgialapphantramkhoi)
│   └── PCB/                      # KiCad projects (Den_coi, Mach_bao_khoi, Nut_nhan_khan_cap)
│
├── New-Fire-Alarm/                # new version of the alarm system
│   ├── README.md
│   ├── fire-dashboard/            # React dashboard (Vite) — real-time alert visualization
│   ├── PCB/Mach_bao_khoi/         # PCB (Altium) for the alarm board
│   ├── main/main.ino
│   └── gui_thongtin_len_lorawan/  # sending data over LoRaWAN
│
├── FireAlarmApp-/                 # Expo/React Native mobile app
│
└── Wireless-Coverage-Prediction/  # ML pipeline for wireless network coverage prediction
    ├── README.md
    ├── data/                      # raw, processed, and terrain data (DEM, landuse)
    └── src/
        ├── api/                   # data retrieval
        ├── processing/            # cleaning, features, terrain
        └── ml/                    # training and prediction (XGBoost)
```

> **Dashboard**: launch it from `fire-dashboard/` with `npm install` (first time only), then `npm run dev` — works on Windows only. WebSocket address to enter: `ws://192.168.55.1:8765`.

---

## 5. Root files

| File                 | Description                                                                     |
| -------------------- | ------------------------------------------------------------------------------- |
| `README.md`        | General overview of the repository                                              |
| `Dockerfile`        | Container configuration for deploying the AI inference system                                              |
| `Running-Tutorial` | Getting-started tutorial: Jetson connection, headless VNC, running the pipeline |
| `fire-detect.py`   | Copy of the detection script (repo root)                                        |
| `.gitignore`       | Files/folders excluded from Git tracking                                        |

---


## 6. System Deployment (Docker Compose)

To ensure high reproducibility and avoid dependency conflicts on the NVIDIA Jetson Orin Nano, the inference system is packaged within a Docker container. 

### Prerequisites on the Jetson
The **NVIDIA Container Runtime**, **Docker**, and **Docker Compose** must be installed (they are included by default in NVIDIA JetPack).

### Run the System
We use Docker Compose to easily manage the hardware bindings (GPU acceleration, network access for the IP camera, and X11 window rendering).

Navigate to the root of this repository (`IOC-DUT`) on the Jetson. 
First, authorize local connections to the X server (this is required to display the video window and only needs to be run once per reboot):

```bash
xhost +local:root
```

Then, build the image and start the container with a single command:

```bash
sudo docker compose up --build
```

This command will automatically execute run.sh, which starts both the WebSocket relay server and the real-time AI fire detection script (fetching the RTSP stream from the IP camera).

### Stop the System
To safely stop the AI, the WebSocket server, and gracefully shut down the Docker container, simply press Ctrl+C in your terminal.


## 7. Quick workflow summary

1. Connect to the Jetson via SSH (see `Running-Tutorial`)
2. Activate headless VNC if graphical access is needed
3. Start the AI on the Jetson using the Docker container (see Section 6 above). This handles both the inference and the WebSocket server.
4. Launch the dashboard on the PC side (`Vietnamese-Code/New-Fire-Alarm/fire-dashboard`) with `npm run dev`
5. Connect the dashboard to the Jetson via `ws://192.168.55.1:8765`
