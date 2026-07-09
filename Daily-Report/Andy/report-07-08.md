
# Report 08/07/2026

We Work on the presentation due to Monday 13th of July. So we have create a powerpoint to explain our works and what we made since the beginning of the internship. We Have also work on the new IA for the Fire detection. Cause of the new model Yolov11m, the Jetson face a Over-current issue. To avoid this issue, we decided to run the IA not on all the frame of the camera but only on few. With this method we have solved this problem.

We are trying to set up the jetson to be accessible by ssh (connection by USB cable) and a vnc.  Pb we have ton set-up headless (without HDMI calbe) so i find this [repo](https://github.com/mauroarcidiacono/jetson-headless-vnc) 

IP : 192.168.55.1

EDID file, use a AOC0000 monitor 1920x1080

commande to lunch the server vnc : x11vnc -usepw -forever -display :0