# Report 03/06/2026

Preamble:
The professor gave us a [Google Sheet](https://docs.google.com/spreadsheets/d/1JbVak5m1N3S0Dq-XeGyO9e7A00-PoN9cihRR5XMIRzQ/edit?gid=1161341563#gid=1161341563) which gathers all the useful links as well as the internship's organization and its different phases. In this document, we also found a link to an Overleaf (LaTeX editor) project, which we are to use to write our end-of-internship report.

## Phase 1

Phase 1 consisted of reading about twenty scientific papers on IOC, fire and smoke detection, and BMS. The goal of this step was to survey everything that had already been done on the subject and explore the range of possibilities. To do this, we searched for articles using search engines such as Google Scholar, IEEE Xplore, and MDPI.com. All the articles are available in the /Documents/Papers section.
We then synthesized the documents by reading the abstract and conclusion of each article to produce the Related Work section. Based on this synthesis, we decided to use YOLOv8 as our AI model.

## Phase 2

### Jetson Orin Nano Configuration

The Jetson Orin Nano needs to have an OS flashed onto it. This OS is provided by NVIDIA and is called JetPack; it is an Ubuntu distribution tailored for the Jetson Orin Nano. For the installation and download of the right OS version, we relied on a [tutorial](https://www.youtube.com/watch?v=4Fc40yt5j4E) and the manufacturer's website. The JetPack version we used is JetPack 6.2.1. Although more recent versions exist (JetPack 7.0), they are intended for Jetson Thor boards.
After flashing the OS, we needed to install the correct build of PyTorch to run our AI. We also relied on the [NVIDIA](https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform/index.html) website for this (to be installed directly on the Jetson afterwards).

We installed jtop, which lets us see, through a graphical interface, the usage percentage of each component and its associated performance (see Gemini discussion).

Once PyTorch was installed and our AI model trained, we needed to convert the .pt file into a .engine file (TensorRT format), a file format specifically designed for the Jetson Orin Nano to achieve better performance.
For this, we used PyTorch as well as Ultralytics, a tool that allows the conversion to be done properly.

### Camera Configuration

To read the camera's video stream, it was important to know the camera's base IP address so we could configure the associated Ethernet port with the right IP address in order to create a subnetwork. For now, we are not using a router because we only have one camera, but if several were to be used, we would need one.
To find out the IP address, we used the SADP software, which allows scanning of the network associated with the computer. We then found the IP address: 192.168.0.123, with a subnet mask of 255.255.255.0.
We then manually configured the port's IP address to 192.168.0.100 (or any other address belonging to the same subnetwork).
We were then able to connect to the camera and configure it (default resolution, motion detection, lighting, etc.).

Once configured, we were able to view the video stream in a web browser by entering the camera's IP address.

For use under Linux, we performed the same operation, manually configuring the IP address of the port to 192.168.0.100. However, we needed to capture and interpret the video stream via a Python script so the AI could read it.
We then wrote a Python script that uses GStreamer to read the video and display it in a graphical window using GTK.

### Merging the AI and the Camera

Now that the AI was operational and we could read the video stream, this video feed needed to be integrated into the AI. We then used another script (available on GitHub) to make the AI work.
After testing, we saw that the AI and the camera interacted well together; however, the AI still needed more precision (it detected LED light as fire).
