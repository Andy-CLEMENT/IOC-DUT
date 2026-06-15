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