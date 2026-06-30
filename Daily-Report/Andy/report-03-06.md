# Report 03/06/2026

Preamble:
The professor gave us a [Google sheet](https://docs.google.com/spreadsheets/d/1JbVak5m1N3S0Dq-XeGyO9e7A00-PoN9cihRR5XMIRzQ/edit?gid=1161341563#gid=1161341563) which gathers all the useful links as well as the organization of the internship, the different phases. In this document we find an Overleaf (LateX editor) for us to write a report of what we produced at the end of the internship.

## Phase 1

phase 1 consisted of reading about twenty scientific documents concerning IOC, fire and smoke detection as well as BMS. With this step, the goal was to sweep everything that was being done on the subject and probe the field of possibilities. For this, we searched for articles using search engines such as Google Scholar and IEE and MDPI.com. All the articles are available in the /Documents/Papers section.
We then synthesized the documents by reading the Abstracts and the conclusions of each article to produce the Related Work part. With this synthesis, we decided to use the AI YOLO8.

## Phase 2

### Jetson Orin Nano Configuration

The Jetson Orin Nano needs to have an OS FLASHED onto it. This OS is provided by Nvdia and is called JetPack, it's an Ubuntu 20.04 distribution mastered for the Jetson Orin Nano. For the installation and download of the right version of the OS, we relied on a [tuto](https://www.youtube.com/watch?v=4Fc40yt5j4E) and the Manufacturer's website. The version of JetPack used is then JetPack 6.2.1. Although more recent versions exist (Jetpack 7.0), they are intended for Jetson Thor cards.
After flashing the OS, you need to install the right distribution of PyTorch to run our AI. We also relied on the [Nvidia](https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform/index.html) website. (Have on the Jetson Afterwards)

Installation of Jtop which allows you to see on a graphical interface the percentage usage of each component and the associated performance. (See Gemini discussion)

Once PyTorch is installed and our AI model trained, we need to transform the .pt into .engine (TensorRT formar), a file format specially designed for the Jetson Nano and to get better performance.
For this we used pytorch as well as unalitycs, a tool that allows the conversion to be done properly

### Camera Configuration

To read the camera's video stream, it was important to know the camera's base IP address, so that we could configure the associated ethernet port with the right IP address in order to create a subnetwork. For now we are not using a router because we have 1 camera but if several were to be used, we would need one.
To find out the IP address we use SADP software which allows scanning the network associated with the computer. We then spotted the IP address: 192.168.0.123 with a mask 255.255.255.0
We then configure the port's IP address manually to 192.168.0.100. (or any other address belonging to the same subnetwork)
We can then connect to it and configure the camera (default definition, motion detection, lighting on, etc);

Once configured we can read the video stream on the web browser by entering the camera's IP address

For use under linux we proceed to the same operation by manually configuring the IP address of port 192.168.0.100. However we need to capture and interpret the video stream via a python script so that the AI can read it.
We then generated a python script which uses Gstream to read the video and display it in a graphical window using gtk.

### Merging the AI and the camera

Now that the AI is operational and we can read the video stream, the reading needs to be integrated into the AI. We then use another script (available on github) which makes the AI work.
After testing, we see that the AI and the camera interact well with each other, however the AI needs a bit more precision (detects led light as fire).
