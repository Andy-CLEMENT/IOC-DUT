from ultralytics import YOLO
import cv2
from pathlib import Path

model = YOLO("runs\\detect\\runs\\detect\\yolo11m_fire_ultimate\\weights\\best.pt")

# Pointe vers ton dossier valid/images du dataset Phase 2 (le plus propre)
val_dir = Path("dataset/valid/images")
output_dir = Path("analyse_erreurs")
output_dir.mkdir(exist_ok=True)

faux_positifs = 0
images = list(val_dir.glob("*.jpg")) + list(val_dir.glob("*.png"))

for img_path in images:
    res = model.predict(str(img_path), conf=0.25, verbose=False)[0]
    
    # Récupère le nom du fichier label correspondant
    label_path = img_path.parent.parent / "labels" / (img_path.stem + ".txt")
    
    # Vérifie si l'image est censée être vide (pas de label)
    est_vide = not label_path.exists() or label_path.stat().st_size == 0
    
    # Cas qui nous intéresse : image vide MAIS le modèle détecte quelque chose
    if est_vide and len(res.boxes) > 0:
        faux_positifs += 1
        img_annotee = res.plot()
        cv2.imwrite(str(output_dir / f"FP_{img_path.name}"), img_annotee)

print(f"\n⚠️  Faux positifs trouvés : {faux_positifs}")
print(f"📁 Images sauvées dans : {output_dir}/")
print("👉 Ouvre ce dossier et regarde ce que le modèle confond avec du feu/fumée")