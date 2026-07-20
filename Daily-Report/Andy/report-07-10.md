 pul

# Report 10/07/2026

We work on the presentation due to Monday, 13th of July. So we have created a powerpoint to explain our work and what we made since the beginning of the internship. We have also worked on the new AI for fire detection. Cause of the new model Yolov11m, the Jetson faces an overcurrent issue. To avoid this issue, we decided to run the AI not on all the frames of the camera but only on a few. With this method we have solved this problem.

Also, we have reworked the python script so that it becomes easier to understand and to maintain. For that we wrote multiple functions to fragment all the functionalities.

Cause we are two groups using the Jetson Nano, we had to share our HDMI-DisplayPort adapter. To avoid issues regarding this sharing, we decided to find a way to access to the Jetson Orin Nano by our PC. TThe official method to do this is to drive the Jetson by SSH (USB-link) and then install a VNC server on it to be able to use the graphic desktop of the Jetson. To do this we followed the official tutorial. However, the Nvidia method suggests connecting a screen to the jetson to activate the VNC server, so we must find a way to activate this "Headless" (without wired connection). While searching the internet, we found a tutorial in this [repo](https://github.com/mauroarcidiacono/jetson-headless-vnc). So we followed it step by step.
To view the Linux Desktop on our PC, we need to use a VNC viewer tool; we chose to use TightVNC, an open source and reliable software for this use.
The configuration can be found below:

```configuration
IP of Jetson : 192.168.55.1 ( put in the dashboard ws://192.168.55.1:8765)
EDID file, use an AOC0000 monitor 1920x1080
commande to launch the server vnc (on the Jetson) : x11vnc - usepw - forever - display :0
```

Then we must run the dashboard on our computer. To set-up the dashboard, you need to be in [/home/andy/repo/IOC-DUT/Vietnamese-Code/New-Fire-Alarm/fire-dashboard] directory and write the following command in the windows terminal (doesn't work on Linux).

```Running-Dashboard
set-up dashboard: npm install (only for first launch)
run the dashboard: npm run dev 

IP to write in the dashboard: ws://192.168.55.1:8765
```
