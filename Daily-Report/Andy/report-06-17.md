
# Report 17/06/2026

We managed to connect the jetson to the Dashboard, which is a big step forward. However we have problems at the level of the script's architecture. Currently the script only sends packets when it detects fire or smoke. When it detects nothing, it doesn't send a packet, which prevents real-time monitoring. We need to modify this.
 address: 192.168.137.202., 8765

 We modified the code and optimized certain lines so that the code is more readable. In addition modifications were made so that the device sends the camera's connection state (ONLINE or OFFLINE) as well as the info on fire and smoke detection (state = "fire" or "smoke"). The Jetson sends a signal every 2 sec to the server which ensures real-time tracking.
 For now, we have installed our server locally on Mr.Martini's PC and connected the jetson to the network created by his computer. We need to succeed in connecting the jetson to the hosted server.

## JSON Frame Format

Here is the format studied:

```format.json
{
    "Camera": "Camera_Anpiz_1",
    "Camera-state": ON,
    "State": "fire",
    "confiance": 65
}
```

Finally we use different format of JSON according to the state of the device. If the camera is offline due to a issue, the JSON format is

```offline.json
{
    "Camera": "Camera_Anpviz_1",
    "online": False,
    "message": "video lost",
    "timestamp": timestamp
}
```

And if the camera is the json is:

```online.json
{
    "Camera": "Camera_Anpviz_1",
    "flame": False,
    "smoke": 100,
    "online": True,
    "timestamp": timestamp
}
```

Unfortunately, the dashboard that we used put our device status as offline if it doesn't recieve a packet in a delay of 5 sec. To avoid this probleme, we send json paquet every 2 sec:

```awake.json
{
    "Camera": "Camera_Anpviz_1",
    "flame": False,
    "smoke": 100,
    "online": True,
    "timestamp": timestamp
}
```

Finally for the everyday use, the JSON that we send is:

```alert.json
{
    "Camera": "Camera_Anpviz_1",
    "state": label,
    "confiance": round(confidence * 100, 2),
    "online": True,
    "timestamp": timestamp,
    "flame": True,
    "smoke": SMOKE_LOW
}
```

"flame" and "smoke" value depend of the device.