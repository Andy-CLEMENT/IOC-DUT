# Note Projet

## Note Hardware

### Note RAK3172

Cette puce est basé sur une puce STM32 et permet la communication en LoRaWAN. Elle possède consomme très peu (usage sur battery) et possède un module de communication longue distance. Il est configurable via l'IDE arduino en passant par les pins UART. Son module longue distance peut être configuré via des commandes AT. L'antenne (50 Ohms minimum) du dispositif est branchée au pin RF de la puce via des connection coaxiaux (J1 et J2 sur KiCad)

### Smoke Sensor

- Bouton poussoir pour reset et reboot (SW1 et SW2)
- J2-> permet de brancher l'antenne au module pour communication LoRaWAN
- RT9013 -> Permet de réguler la tension et de toujours avoir 3.3V4
- PA10 -> Connecté au transistor Q2 et s'active lorsqu'il y a de la fumée ( On a une légére variation de courant INA+ / INA-)
- LMV358 utilisé pour amplifie le courant généré par une légère variation de courant. Il sera connecté au port ADC du module pour échantilloné avec le ADC.
- Connector sont des broches de communications

### Button

- Broche PA10 permet est connecté au boutton. Dispositif anti-rebond (C11 et R17)
- BAV99 -> Protection d'electricité statique car boutton à l'exterieur du PCB.
- Transistor Q1 permet de piloter le Buffer avec le port PA10

### Lampe/Sireine

- 2 transistors Q1 et Q2 qui permettent d'utiliser le courrant de l'alimentation pour actionner la sirène car le courant du pin PA0 est trop faible. Le transistors sont utilisés comme robinet qui redirige le courant.

## Note software

### Code du RK3172 main

On a une machine à états (en alert et ou safe). Lorsque le l'état est safe, le moudle entre ne mode **Deep Sleep** pendant 15 sec. Une fois réveiller il mesure utilise plusieurs fois le capteur IR du detecteur pour vérifier s'il n'y a pas de fumée. Si le nombre de detections est au dessus de 4, le module switch en mode alert et envoit les données au serveur. Pour sortir de l'état alerte, il mesure s'il y a de la fumée et si il y en a pas, on décrémente le compteur de detection. Une fois arrivé à 0, on retourne à l'état safe le code utilise des fonctions intégrées et interprétées par le module RK3172 (api.lorawan.exemple()).