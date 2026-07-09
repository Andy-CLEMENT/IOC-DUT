from ultralytics import YOLO

def main():
    model = YOLO("yolo11m.pt")

    print("Training begins...")

    results = model.train(
        data="dataset/data.yaml",

        epochs=100,
        patience=20,
        
        imgsz=640,
        batch=8,
        device=0,
        workers=8,

        optimizer="SGD",
        lr0=0.01,
        momentum=0.937,
        weight_decay=0.0005,

        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        fliplr=0.5,
        mosaic=1.0,
        close_mosaic=15,


        project="runs/detect",
        name="yolo11m_fire_v4",
        exist_ok=True,
    )

    print(f"Training completed !")
    print(f"mAP50 final : {results.box.map50:.4f}")

if __name__ == '__main__':
    main()