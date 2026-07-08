
# Report 23/06/2026

We must now merge the project with the Vietnamese one and measure the perfs. Improve the model. The Vietnamese must help us create a real fire and real smoke to test our device in real conditions.

We then decided to switch to a yolo11 medium model. This model is more performant and less energy-hungry than the yolov8 s. Our goal is to reach at least 90% prediction accuracy, currently we are at 84%, which is insufficient.

With the model change (yolo11 m) and the increase of the dataset (13,000 to 24,000 with modification of existing images), notably neon images. Neons were detected as fire. With this increase, we got 87% accuracy, which falls short of expectations.
To further improve accuracy, we need to feed the original dataset with other images.

We also shared the project with the Vietnamese so they can connect our project to theirs.