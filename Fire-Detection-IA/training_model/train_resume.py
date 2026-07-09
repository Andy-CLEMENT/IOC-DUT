from ultralytics import YOLO

def main():
    model = YOLO("runs\\detect\\runs\\detect\\yolo11m_fire_v4\\weights\\last.pt") 

    print(" Reprise de l'entraînement là où il s'est arrêté...")
    
    results = model.train(resume=True)
    
    print(" Entraînement terminé !!!")

if __name__ == '__main__':
    main()