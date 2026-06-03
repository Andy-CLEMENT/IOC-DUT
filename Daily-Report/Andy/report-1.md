# Report 03/06/2026

Preambule:
Le professeur nous a donné un [Google sheet](https://docs.google.com/spreadsheets/d/1JbVak5m1N3S0Dq-XeGyO9e7A00-PoN9cihRR5XMIRzQ/edit?gid=1161341563#gid=1161341563) qui regroupe tous les liens utiles ainsi l'organisation du stage, les différentes phases. Dans se document on retrouve un Overleaf (editeur LateX) pour que l'on écrive un compte rendu de ce que l'on a produit à la fin du stage.

## Phase 1

la phase 1 consistait à lire une vingtaine de document scientifiques concernant les IOC, la detection de feu et de fumée ainsi que les BMS. Avec cette étape, le but était de balayer tous ce qui se faisait en la matière et de soder le champs des possibles. Pour cela, nous avons chercher les articles en utlisant des moteurs de recherche tel que Google Scholar et IEE et MDPI.com. Tous les articles sont disponible dans la rubrique /Documents/Papers.
Nous avons alors synthétisé les documents en lisant les Abstracts et les conclusion de chaque article pour produire la partie Related Work. Avec cette synthése, nous avons décidé d'utiliser l'IA YOLO8.

## Phase 2

### Configuration Jetson Orin Nano

La Jetson Orin Nano a besoin que l'on FLASH son un OS. Cette OS est fournis par Nvdia et se nomme JetPack, c'est une distribution Ubuntu 20.04 masterisé pour la Jetson Orin Nano. Pour l'installation et le téléchargement de la bonne version de de l'OS, on s'est appuyé sur un [tuto](https://www.youtube.com/watch?v=4Fc40yt5j4E) et le site Constructeur. La Version de JetPack utilisé et alors JetPack 6.2.1. Bien qu'il existe des versions plus récentes (Jetpack 7.0), elles sont destiné aux carte Jetson Thor.
Après avoir flashé l'OS, Il faut installer la bonne distribution de PyTorch pour faire fonctionner notre IA. On s'appuit également sur le site de [Nvidia](https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform/index.html). (Avoir sur la Jetson Après)

Installation de Jtop qui permet de voir sur une interface graphique le pourçentage d'utilisation de chaque composants et les performances associé. (Voir discussion Gemini)

Une fois que PyTorch installé et notre model d'IA entrainé, nous devons transformer le .pt en .engine (formar TensorRT), unformat de fichier spécialement conçu pour la Jetson Nano et avoir de meilleur performance.
Pour cela on a utilisé pytorch ainsi que unalitycs, un outils qui permet de faire la conversion proprement

### Configuration Camera

Pour lire le flux video de la caméra, il était important de connaitre l'adresse IP de base de la caméra, pour que l'on puisse configurer le port ethernet associé avec la bonne adresse IP afin de créer un sous réseau. Pour l'instant nous n'utilisons pas de routeur car nous avons 1 caméra mais si plusieurs venait à être utilisées, nous en aurions besoin.
Pour connaitre l'adresse IP nous utilisons un logiciel SADP qui permet de scanner le réseau assocé à l'ordinateur. On a alors repéré l'adresse IP : 192.168.0.123 avec un masque 255.255.255.0
On configure alors l'adresse IP du port manuellement en 192.168.0.100. ( ou tou auatre adress qui appartient au même sous réseaux)
On peut alors s'y connecter et configurer la caméra (definition par défaut, detection de mouvement, allumage de l'éclairage, ect);

Une fois configurer on peut lire le flux video sur le navigateur web en saisissant l'adresse IP de la caméra

Pour une utilisation sous linux nous précédons à la même opération en configurant manuellement l'address IP du port 192.168.0.100. Cependant nous devons relever et interpréter le flux video via un script python pour que l'IA puisse la lire.
On a lors généré un script python qui utilise Gstream pour lire la video et l"affiché dans une fenêtre graphique à l'aide de gtk.

### Merge de l'IA et de la caméra

Maintenant que l'IA et opérationnel et que l'on peut lire le flux video, Il faut intégrer la lecture à l'IA. On utlise alors un autre script (disponible sur github) qui permet de faire fonctionner l'IA. 
Après essaie, on voit que l'IA et la caméra interagisse bien entre eux, cependant l'IA a besoin d'un peu plus de précision ( detecte le lumière led comme du feu).
