# To-Do

## Camera

- The camera can be powered by a 12V external power supply. The Ethernet port will be used to share the video stream with the Jetson Orin Nano. We are considering this solution because the Jetson Nano's Ethernet port does not support PoE; it is only programmed for data transfer.

- Configure the camera directly with the Jetson Nano (OS base on Linux).

## Jetson

[Link](https://developer.nvidia.com/embedded/jetpack) to the Constructor Website

- Configure and Install The Software with Balena Etcher
We use the JetPack 6.2.1 for the configuration according to this [web-site](https://developer.nvidia.com/embedded/jetpack-archive). To have a healthy installation, we have to chek if the firmware is above 36. (we have 36.4.3)

## Material to Have

- Alimentation 12V for camera and 19.5V for Jetson ( We can pic a alimentation of 20V and put a voltage reduction)
- high-speed microSD card (64GB or larger) or a NVMe SSD
- STM32 Card to rework alarm system
