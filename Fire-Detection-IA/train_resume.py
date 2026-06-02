from ultralytics import YOLO

def main():

    model = YOLO("runs/detect/yolov8s_fire_day_IR_model/weights/last.pt") #YOLOv8 small

    print("Resuming training...")
    
    results = model.train(
        resume=True
    )
    
    print("Training completed !!!")

if __name__ == '__main__':
    main()