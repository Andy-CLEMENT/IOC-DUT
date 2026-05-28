# Note Projet

## Note Hardware

### Note RAK3172

Cette puce est basé sur une puce STM32 et permet la communication en LoRaWAN. Elle possède consomme très peu (usage sur battery) et possède un module de communication longue distance. Il est configurable via l'IDE arduino en passant par les pins UART. Son module longue distance peut être configuré via des commandes AT. L'antenne (50 Ohms minimum) du dispositif est branchée au pin RF de la puce via des connection coaxiaux (J1 et J2 sur KiCad)

### Smoke Sensor

- Bouton poussoir pour reset et reboot (SW1 et SW2)
- J2-> permet de brancher l'antenne au module pour communication LoRaWAN
- RT9013 -> Permet de réguler la tension et de toujours avoir 3.3V.
- PA10 -> Connecté au transistor Q2 et s'active lorsqu'il y a de la fumée ( On a une légére variation de courant INA+ / INA-)
- LMV358 utilisé pour amplifie le courant généré par une légère variation de courant. Il sera connecté au port ADC du module pour échantilloné avec le ADC.
- Connector sont des broches de communications
- J3 est la broche d'alimentation de la pile AAA, la tension de sortie est VCC. On a une diode D3 de protection du circuit. On utilise un pont diviseur pour ne pas griller le RT9013.
- Pour le circuit amplificateur, on utilise 2 AOP pour INA et INB et un diviseur de tension  (R8 et R9) pour avoir la tension négative ( on sait que la tension d'entrée est de 0-3.3V). Filtrage passe-bas (C8 et R11) : Le condensateur C8 (100 nF) placé en parallèle avec la résistance R11 (10 kΩ) forme un filtre actif. Son rôle est d'éliminer les parasites à haute fréquence (le bruit électrique, les interférences radio du module LoRaWAN) pour ne laisser passer que les variations très lentes de tension causées par l'accumulation de fumée. OUTB est la sortie clean du circuit, elle est lu par.

### Button

- Broche PA10 permet est connecté au boutton. Dispositif anti-rebond (C11 et R17)
- BAV99 -> Protection d'electricité statique car boutton à l'exterieur du PCB.
- Transistor Q1 permet de piloter le Buffer avec le port PA10

### Lampe/Sireine

- 2 transistors Q1 et Q2 qui permettent d'utiliser le courrant de l'alimentation pour actionner la sirène car le courant du pin PA0 est trop faible. Le transistors sont utilisés comme robinet qui redirige le courant.

## Note software

### Code du RK3172 main

On a une machine à états (en alert et ou safe). Lorsque le l'état est safe, le moudle entre ne mode **Deep Sleep** pendant 15 sec. Une fois réveiller il mesure utilise plusieurs fois le capteur IR du detecteur pour vérifier s'il n'y a pas de fumée. Si le nombre de detections est au dessus de 4, le module switch en mode alert et envoit les données au serveur. Pour sortir de l'état alerte, il mesure s'il y a de la fumée et si il y en a pas, on décrémente le compteur de detection. Une fois arrivé à 0, on retourne à l'état safe le code utilise des fonctions intégrées et interprétées par le module RK3172 (api.lorawan.exemple()).