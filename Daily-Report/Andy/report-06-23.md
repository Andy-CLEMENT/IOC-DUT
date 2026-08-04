# Report 23/06/2026

We must now merge our project with the Vietnamese team's and measure the performance, then improve the model. The Vietnamese team must help us create a real fire and real smoke to test our device in real conditions.

We then decided to switch to a YOLO11 Medium model. This model is more performant and less energy-hungry than YOLOv8s. Our goal is to reach at least 90% prediction accuracy; we are currently at 84%, which is insufficient.

With the model change (YOLO11m) and the increase of the dataset (from 13,000 to 24,000 images, including modifications of existing images), notably images of neon lights — which were being detected as fire — we reached 87% accuracy, which still falls short of expectations.
To further improve accuracy, we need to expand the original dataset with additional images.

We also shared the project with the Vietnamese team so they can connect our project to theirs.
