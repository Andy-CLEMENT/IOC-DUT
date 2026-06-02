import torch

def fix_model():
    # 1. Le chemin vers ton modèle inversé
    original_model_path = r"C:\Users\Alexis\Desktop\projet\IOC-DUT\Fire-Detection-IA\runs\detect\runs\detect\yolov8s_fire_day_IR_model-3\weights\best.pt"
    
    # Le chemin pour sauvegarder le modèle corrigé
    fixed_model_path = r"C:\Users\Alexis\Desktop\projet\IOC-DUT\Fire-Detection-IA\runs\detect\runs\detect\yolov8s_fire_day_IR_model-3\weights\best_fixed.pt"

    print("Ouverture du modèle...")
    # On charge l'archive PyTorch
    ckpt = torch.load(original_model_path)

    # 2. On regarde les noms actuels (ça devrait afficher {0: 'fire', 1: 'smoke'})
    print("Anciens labels :", ckpt['model'].names)

    # 3. La chirurgie : On inverse !
    ckpt['model'].names = {0: 'smoke', 1: 'fire'}

    # 4. On sauvegarde le nouveau fichier
    torch.save(ckpt, fixed_model_path)
    
    print(f"Opération réussie ! Les nouveaux labels sont : {ckpt['model'].names}")
    print(f"Nouveau modèle sauvegardé ici : {fixed_model_path}")

if __name__ == '__main__':
    fix_model()