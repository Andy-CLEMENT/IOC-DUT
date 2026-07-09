from ultralytics import YOLO

def main():
    model = YOLO("yolo11m.pt") #YOLOv11 medium

    print("Training begins...")
    
    results = model.train(
        data="dataset/data.yaml",
        epochs=150,
        patience=25,
        imgsz=640,
        batch=8,
        device=0,
        workers=8,
        cos_lr=True,
        cache=True,
        close_mosaic=15,
        project="runs/detect",
        name="yolo11m_fire_final"
    )
    
    print("Training completed !!!")

if __name__ == '__main__':
    main()