# Report 23/06/2026

On doit maitenant merge le projet avec  celui des vietnamiens et mesurer les perfs. Ameliorer le modèle. Les vietnamiens doivent nous aider à créer un vrai feu et de la vrai fumée pour tester en condition réelle notre dispositif.

Nous avons alors décider de basculer sur un model yolo11 medium. Ce model est plus performant et moins energivore que le yolov8 s. Notre objectif est d'atteidnre au moins 90% de précision de prédiction, actuellement nous sommes à 84%, ce qui est insuffisant.

Avec le changement de model (yolo11 m) et l'augmentation de la dataset (13 000 à 24 000 avec modification des images existante), notamment d'image de néon. Les néons étaient detecté comme du feu. Avec cette augmentation, nous avons eu 87% de précision, ce qui est en-deca des attentes.
Pour encore améliorer la précision, nous devons alimenter la dataset d'origine avec d'autres images.

Nous avons également partager le projet avec les vietnamiens pour qu'il puisse connecter notre projet au leur.
