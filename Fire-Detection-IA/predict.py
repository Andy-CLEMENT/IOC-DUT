from ultralytics import YOLO

def main():
    model_path = r"C:\Users\Alexis\Desktop\projet\IOC-DUT\Fire-Detection-IA\model_final\best.pt"

    print("Chargement de l'IA...")
    model = YOLO(model_path)

    dossier_test = r"C:\Users\Alexis\Desktop\projet\IOC-DUT\Fire-Detection-IA\test_after_training"

    print(f"Début de la boucle d'analyse sur le dossier : {dossier_test}")
    
    results = model.predict(
        source=dossier_test,
        conf=0.4,
        show=True,
        save=True
    )

    print("\nAnalyse terminée ! Toutes tes images annotées sont sauvegardées.")
    print("Regarde dans le dossier : runs/detect/predict/")

if __name__ == '__main__':
    main()