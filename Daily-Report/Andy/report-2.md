# Report 15/06/2026

## Weeckly meeting

On doit refaire le Diagramme de methodologie, on doit le rendre plus précis (fait)
On doit aussi mettre a jour le planning est s'y tenir, cela permet au tuteur de suivre notre progression est de voir les tâches à accomplir et déjà accomplies.

Test: Essai du code qui permet d'envoyer une alerte
Determination de la tram JSON à envoyer

## Format de la trame JSON

Voici le format étudié:

```format.json
{
    "Camera": "Camera_Anpiz_1",
    "Camera-state": ON,
    "State": "fire",
    "confiance": 65
}
```
## Implémentation du code

J'ai implémenter le code d'Alexis qui permet d'envoyer une alerte d'incendie à un serveur pour que l'on puisse le mettre en place sur le dashboard. J'ai également ajouté une fonctionnalité qui permet de rechercher la connection o la camera lorsque l'on ne la reconnait pas.

# Report 17/06/2026

On a reussi a connecter la jetson au Dashboard, ce qui est une grande avancé. Cependant nous avons des problèmes au niveau de l'architecture du script. Actuellement le sript fais en sorte d'envoyer des paquets seulement lorsqu'elle detecte du feu ou de la fumée. Lorsqu'elle ne detecte rien, elle n'envoie pas de paquet, ce qui empêche la surveillance en temps réel. Nous devons modifier cela.
 adresse : 192.168.137.202., 8765

 Nous avons modifer le code et optimiser certaine ligne pour que le code soit plus lisible. De plus des modifications ont été apporté pour que le dispositif envoie l'état de connection de la caméra (ONLINE ou OFFLINE) ainsi que les infos sur la detection du feu et de la fumée (state = "fire" ou "smoke"). La Jetson envoie un signal tous les 2 sec au serveur ce qui assure un suivi en temps réel. 
 Pour le moment, nous avons installer notre serveur localement sur le PC de Mr.Martini et connecté la jeston au réseau créée par son ordinateur. Il faut que nous reussissons à connecter la jetson au serveur hebergé.
