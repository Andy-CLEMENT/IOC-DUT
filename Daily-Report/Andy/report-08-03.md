# Report 03/08/2026

Our tutor asked us to finalize the source code and package it in a Docker container, with a Dockerfile, so the project can be submitted and run on any Jetson Orin Nano without manually reinstalling every dependency by hand. We spent most of the day on this, since Docker on Jetson turned out to be a lot more finicky than on a regular PC.

The first attempt used `ultralytics/ultralytics:latest-arm64` as the base image, which builds `apt-get install` failed on `libgl1-mesa-glx` (package removed in newer Ubuntu). After investigating, we found out this image is actually a generic ARM64 build meant for Raspberry Pi, not Jetson: no CUDA, no TensorRT, and none of the NVIDIA GStreamer plugins (`nvv4l2decoder`, `nvvidconv`) our camera pipeline needs. We switched to `ultralytics/ultralytics:latest-jetson-jetpack6`, which is built on top of NVIDIA's official L4T image and matches our JetPack 6 setup.

Even with the right base image, the camera still refused to connect inside the container. We debugged this step by step using `gst-launch-1.0` directly (bypassing Python/OpenCV, which silently swallows GStreamer errors) and found two separate issues stacked on top of each other:
- the NVIDIA hardware-accelerated GStreamer elements need EGL, which needs to authenticate against the host's X11 server, even with no window displayed. Fixed with `xhost +local:root` before starting the container.
- the OpenCV bundled in the base image has 0 GStreamer plugins compiled in (confirmed via `OPENCV_VIDEOIO_DEBUG=1`). We ended up mounting the host's own OpenCV `.so` (already working outside Docker) into the container, along with its dependent libraries (`libopencv_*.so`, `libgdal.so.30`), instead of trying to rebuild OpenCV with GStreamer support from scratch.

Once the camera and inference were working, we also fixed a few smaller things: `cv2.imshow` doesn't work in the container (headless OpenCV), so we made the display window optional via a `SHOW_WINDOW` environment variable; the relay server's WebSocket URL was pointing to the wrong host; and we added the missing `websocket-client`/`websockets` Python packages to the Dockerfile (two different libraries, easy to confuse).

We wrote a short launch tutorial (`Running-Tutorial.md`) covering the startup procedure and a troubleshooting section listing every issue above, for teammates who don't know the project's Docker setup yet.

```configuration
Launch (every session, after a reboot/logout):
  xhost +local:root
  docker compose up --build
```
