from ultralytics import YOLO

def main():
    # On repart du modèle de base pour appliquer la nouvelle stratégie globale
    model = YOLO("yolo11m.pt") 

    print("Training begins...")
    
    results = model.train(
        data="dataset/data.yaml",
        epochs=150,    
        patience=30,
        imgsz=640,
        batch=8,
        device=0,
        workers=8,
        
        optimizer="AdamW",
        lr0=0.001,
        cos_lr=True,
        close_mosaic=20,
        
        project="runs/detect",
        name="yolo11m_fire_ultimate"
    )
    
    print("Training completed !!!")

if __name__ == '__main__':
    main()