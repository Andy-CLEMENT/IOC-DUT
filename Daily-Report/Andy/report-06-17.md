# Report 17/06/2026

We managed to connect the Jetson to the dashboard, which is a big step forward. However, we are having issues with the script's architecture. Currently, the script only sends a packet when it detects fire or smoke. When it detects nothing, it does not send a packet, which prevents real-time monitoring. We need to fix this.

Address: 192.168.137.202, port 8765

We modified the code and optimized certain lines to make it more readable. In addition, changes were made so that the device sends the camera's connection state (ONLINE or OFFLINE) as well as the fire/smoke detection info (state = "fire" or "smoke"). The Jetson sends a signal to the server every 2 seconds, which ensures real-time tracking.
For now, we have installed our server locally on Mr. Martini's PC and connected the Jetson to the network created by his computer. We still need to connect the Jetson to the hosted server.

## JSON Frame Format

Here is the format we studied:

```format.json
{
    "Camera": "Camera_Anpviz_1",
    "Camera-state": "ON",
    "State": "fire",
    "confiance": 65
}
```

We ultimately use different JSON formats depending on the device's state. If the camera is offline due to an issue, the JSON format is:

```offline.json
{
    "Camera": "Camera_Anpviz_1",
    "online": false,
    "message": "video lost",
    "timestamp": timestamp
}
```

And if the camera is online, the JSON is:

```online.json
{
    "Camera": "Camera_Anpviz_1",
    "flame": false,
    "smoke": 100,
    "online": true,
    "timestamp": timestamp
}
```

Unfortunately, the dashboard we use marks our device as offline if it does not receive a packet within 5 seconds. To avoid this problem, we send a JSON packet every 2 seconds:

```awake.json
{
    "Camera": "Camera_Anpviz_1",
    "flame": false,
    "smoke": 100,
    "online": true,
    "timestamp": timestamp
}
```

Finally, for everyday use, the JSON we send is:

```alert.json
{
    "Camera": "Camera_Anpviz_1",
    "state": label,
    "confiance": round(confidence * 100, 2),
    "online": true,
    "timestamp": timestamp,
    "flame": true,
    "smoke": SMOKE_LOW
}
```

The "flame" and "smoke" values depend on the device's state.
