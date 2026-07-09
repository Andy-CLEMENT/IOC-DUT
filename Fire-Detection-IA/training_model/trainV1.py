from ultralytics import YOLO

def main():
    model = YOLO("weights/yolov8s.pt") #YOLOv8 small

    print("Training begins...")
    
    results = model.train(
        data="dataset/data.yaml",
        epochs=50,
        imgsz=640, # image size
        batch=16,
        device=0,
        workers=4, # cpu threads
        project="runs/detect",
        name="yolov8s_fire_day_IR_model" #save directory
    )
    
    print("Training completed !!!")

if __name__ == '__main__':
    main()