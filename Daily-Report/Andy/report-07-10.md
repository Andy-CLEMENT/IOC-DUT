# Report 10/07/2026

We worked on the presentation due on Monday, July 13th. We created a PowerPoint to explain our work and what we have achieved since the beginning of the internship. We also worked on the new AI for fire detection. Because of the new YOLOv11m model, the Jetson faces an overcurrent issue. To avoid this issue, we decided to run the AI not on every frame from the camera, but only on a few of them. This method solved the problem.

We also reworked the Python script to make it easier to understand and maintain. To do this, we wrote multiple functions to split up the different functionalities.

Because two groups are using the Jetson Orin Nano, we had to share our HDMI-to-DisplayPort adapter. To avoid issues related to this sharing, we decided to find a way to access the Jetson Orin Nano from our PC. The official method for this is to access the Jetson via SSH (over a USB link) and then install a VNC server on it to access its graphical desktop. We followed the official tutorial to do this. However, NVIDIA's method assumes a screen is connected to the Jetson to activate the VNC server, so we had to find a way to enable this "headless" mode (without a wired display connection). While searching online, we found a tutorial in this [repo](https://github.com/mauroarcidiacono/jetson-headless-vnc), which we followed step by step.
To view the Jetson's Linux desktop on our PC, we needed a VNC viewer tool; we chose TightVNC, a reliable open-source software for this purpose.
The configuration can be found below:

```configuration
IP of Jetson: 192.168.55.1 (put in the dashboard as ws://192.168.55.1:8765)
EDID file: use an AOC0000 monitor, 1920x1080
Command to launch the VNC server (on the Jetson): x11vnc -usepw -forever -display :0
```

We then had to run the dashboard on our computer. To set up the dashboard, you need to be in the [/home/andy/repo/IOC-DUT/Vietnamese-Code/New-Fire-Alarm/fire-dashboard] directory and run the following commands in a Windows terminal (this does not work on Linux).

```Running-Dashboard
Set up dashboard: npm install (first launch only)
Run the dashboard: npm run dev

IP to enter in the dashboard: ws://192.168.55.1:8765
```
