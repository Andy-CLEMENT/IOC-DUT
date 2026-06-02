from ultralytics import YOLO

def main():
    # 1. Charger ton modèle fraîchement entraîné
    # J'ai repris le chemin exact généré dans ton terminal tout à l'heure
    model_path = "runs\\detect\\runs\\detect\\yolov8s_fire_day_IR_model-3\\weights\\best.pt"
    
    print("Chargement de l'IA...")
    model = YOLO(model_path)

    # 2. Choisir l'image ou la vidéo à tester
    source_test = "test-fire7.jpg" # Modifie le nom si ta photo s'appelle autrement

    # 3. Lancer la prédiction
    print(f"Analyse de {source_test} en cours...")
    results = model.predict(
        source=source_test,
        conf=0.4,       # Seuil de confiance : n'affiche que les détections > 40%
        show=True,      # Ouvre une fenêtre pour afficher l'image annotée en direct
        save=True       # Sauvegarde le résultat dans le dossier runs/detect/predict/
    )

    print("Analyse terminée ! Regarde l'image.")

if __name__ == '__main__':
    main()