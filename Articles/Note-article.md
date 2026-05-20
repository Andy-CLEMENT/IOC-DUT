# Note article

## : Mobile Network Coverage Prediction Using Multi-Modal Model Based on Deep Neural Networks and Semantic Segmentation (2024)

Dans cette article, on étudit une méthode qui permet d'estimer la perte de puissance des signaux radios dans différents environnemen en ce basant sur des images sattelites et coordonnées GPS. L'IA en charge de cette analyse estime la perte de signal du à l'environement autour. On a une erreur de seulement 1.93dB, ce qui est très peu.

- **1. Le contexte et le défi des modèles traditionnels**
Historiquement, pour savoir jusqu'où porte le signal d'une antenne relais (station de base), les ingénieurs utilisent des "modèles de perte de chemin" (path loss models).
Le problème : Ces modèles nécessitent de connaître avec précision les paramètres de l'antenne : sa hauteur exacte, son inclinaison (tilt), sa puissance d'émission, etc. Or, ces données sont souvent confidentielles, détenues par les opérateurs, ou parfois obsolètes dans les bases de données.
De plus, les modèles traditionnels simplifient souvent trop l'environnement (par exemple en considérant qu'une zone est globalement "urbaine" ou "rurale"), ou nécessitent des modélisations 3D des bâtiments extrêmement coûteuses à réaliser (comme le Ray-Tracing).

- **2. L'idée novatrice : regarder depuis l'espace**
Puisque les obstacles physiques (bâtiments, forêts, collines) sont les principaux responsables de la perte de signal, les auteurs ont eu l'idée d'utiliser des images satellites en haute résolution.
Au lieu de demander à l'opérateur les paramètres de son antenne, le modèle va "apprendre" de lui-même comment l'environnement visible sur l'image satellite affecte le signal entre le point A (l'antenne) et le point B (le smartphone de l'utilisateur).

- **3. L'architecture de la solution (Comment ça marche ?)**
Les chercheurs ont créé un modèle "multimodal" nommé DNN-SS, ce qui signifie qu'il combine plusieurs types de données (images et coordonnées) grâce à l'intelligence artificielle. Voici les 3 étapes clés de son fonctionnement :
La Segmentation Sémantique (OCRNet) : Le système extrait une image satellite de la zone située entre l'antenne et l'utilisateur. Un réseau de neurones spécialisé dans l'analyse d'images (OCRNet) scanne cette image et classe chaque pixel : il identifie où sont les bâtiments, les routes, les arbres, l'eau, etc. Il transforme l'image brute en une véritable "carte des obstacles".
Le filtrage des données (Bruit) : Les données de signal utilisées pour entraîner l'IA proviennent de mesures participatives (crowdsourcing via des smartphones). Comme ces données sont très instables (un utilisateur peut être dans sa poche, dans une voiture, etc.), les auteurs appliquent un algorithme de "moyenne mobile spatio-temporelle" pour lisser les valeurs et éliminer les erreurs aberrantes.
Le Réseau de Neurones Profonds (DNN) : C'est le cerveau final. Il prend en entrée les caractéristiques extraites de l'image satellite (la carte des obstacles) ET les distances géographiques exactes (latitude/longitude de l'antenne et de l'utilisateur). Il fusionne ces informations pour calculer la puissance exacte du signal reçu (le RSRP) au point demandé.

- **4. Expérimentations et résultats marquants**
L'algorithme a été testé sur le campus de l'Université de Pékin (BUPT), un environnement urbain complexe avec beaucoup de bâtiments et de végétation.
Précision : Le modèle a atteint une erreur quadratique moyenne (RMSE) de seulement 1,97 dB, ce qui est exceptionnellement précis (les modèles traditionnels oscillent souvent entre 5 et 8 dB d'erreur).

Le point fort (Généralisation) : La plus grande victoire de cette étude réside dans ses tests sur des "zones d'exclusion". Les chercheurs ont demandé au modèle de prédire la couverture dans des quartiers où absolument aucune mesure n'avait été fournie lors de l'entraînement. Grâce à sa compréhension de l'image satellite, l'IA a été capable de déduire que derrière tel type de bâtiment, le signal allait logiquement chuter, prouvant qu'elle avait réellement appris la physique de la propagation radio et non pas juste mémorisé les données.

Limites (Le "Research Gap" pour justifier ton projet) :
La complexité de cette méthode est très élevée (nécessite des images satellites, du traitement d'image lourd, des modèles de Deep Learning très gourmands en ressources). Elle est difficilement applicable telle quelle dans un contexte de déploiement IoT LoRa, où les nœuds sont limités en puissance et où on cherche une solution "on-the-fly".
Pour ton article : Cet article est excellent pour montrer que tu connais les tendances actuelles de la recherche. Tu peux l'utiliser pour dire : « Alors que les tendances actuelles en prédiction de couverture s'orientent vers des modèles multi-modaux complexes nécessitant une puissance de calcul importante (Deep Learning sur images satellites), notre approche propose une alternative plus pragmatique et autonome pour l'IoT. En couplant la multilatération (MTL) et le Random Forest, nous atteignons une précision élevée tout en maintenant une efficacité énergétique et matérielle compatible avec un déploiement sur une plateforme Edge (Jetson Nano), rendant la localisation intelligente accessible sans avoir besoin d'infrastructures cloud lourdes ou d'imagerie complexe. »

## Fixed Rank Kriging for Cellular Coverage Analysis (2015-2016)

Dans cette article, on mesure la vouvertue en utilisant les appareils sur le terrain. Les ordinateurs et smartphone mesure la puissance du signal et envoie leur coordonée gps pour qu'une estimation de la couvertur ce fasse. Le problèmes et que cette méthode est gourmande en calcule. Ces chercheus on trouvé un algorithme moins gourmand en calcule mais qui se repose toujour sur la mesures d'appareil. Avec cette méthode, il est possible de mesurer la couverture réseau d'une ville "gratuitement".

- **1. Le contexte et le défi des données massives**
L'optimisation et la planification de la couverture sont des tâches primordiales pour tout opérateur de réseau mobile. Pour ce faire, les opérateurs s'appuyaient traditionnellement sur des campagnes de "Drive Tests", très onéreuses à réaliser.  Pour réduire ces coûts, une fonctionnalité du standard 3GPP nommée MDT (Minimization of Drive Tests) a été introduite. Elle permet aux terminaux des utilisateurs d'envoyer automatiquement au réseau leurs mesures de signal radio, couplées à leur position géographique (GPS).  Bien que cela crée une source d'information très riche, un grand défi persiste : il reste indispensable de prédire la couverture radio dans les zones où aucun utilisateur ne s'est encore rendu (et où aucune mesure n'est donc disponible).

- **2. Le problème mathématique de l'interpolation spatiale**
Pour estimer la puissance du signal dans ces "zones vides", les scientifiques utilisent le Krigeage (Kriging). Il s'agit d'une technique d'interpolation spatiale très performante pour générer des cartes de couverture continues à partir de mesures éparses.  Cependant, le Krigeage classique devient inexploitable à grande échelle. Son coût de calcul mathématique est de $O(N^3)$, où $N$ représente le nombre total de points de mesure.  Face aux volumes massifs de données générées par les téléphones via la technologie MDT, cette méthode classique est beaucoup trop lourde et mettrait trop de temps à s'exécuter.

- **3. La solution proposée : le Fixed Rank Kriging (FRK)**
Pour contourner cette limite de puissance de calcul, les chercheurs ont appliqué et adapté une variante statistique spécifique appelée Fixed Rank Kriging (FRK), ou Krigeage de rang fixe.  Cette approche repose sur un modèle d'effets spatiaux qui permet d'estimer les données sans avoir à manipuler des matrices mathématiques géantes. L'objectif principal de l'article est de réduire cette complexité informatique tout en préservant une qualité de prédiction acceptable pour l'opérateur.  Les auteurs ont également formulé une méthode d'estimation du "Maximum de Vraisemblance" (ML - Maximum Likelihood) spécialement dérivée pour ajuster les paramètres inconnus de ce modèle radio.  

- **4. Expérimentations et résultats sur le réseau LTE**
L'algorithme a été rigoureusement évalué en utilisant à la fois des mesures simulées par ordinateur et de véritables mesures de terrain issues d'un réseau 4G LTE.  Les expériences démontrent que le FRK offre un excellent compromis entre la précision des prédictions de signal et le niveau de complexité informatique requis.  Enfin, pour se rapprocher de la réalité opérationnelle des réseaux, les chercheurs ont validé leur solution sur un scénario plus complexe impliquant de multiples cellules (Multicellular use-case) dotées d'antennes directives. Dans cette configuration, le modèle FRK a démontré de très bonnes performances non seulement pour prédire la carte globale de couverture, mais aussi pour identifier avec précision la meilleure cellule serveuse ("best serving cell") pour un point géographique donné.

Limites (Le "Research Gap" pour justifier ton projet) :
L'étude se concentre exclusivement sur les réseaux cellulaires LTE, qui sont très différents des réseaux IoT. Bien que le FRK réduise la complexité par rapport au Krigeage classique, cela reste une méthode mathématique lourde conçue pour de grandes quantités de données cellulaires centralisées.
Pour ton article : Cela te permet de justifier que pour des réseaux de capteurs sans fil (WSN) basse consommation comme LoRa, il faut une approche encore plus frugale en énergie et en calcul. Votre utilisation de la multilatération (MTL) combinée à un algorithme de Machine Learning (Random Forest) exécuté localement sur une Jetson Nano (Edge Computing) est beaucoup plus adaptée aux contraintes matérielles de l'IoT que les méthodes géostatistiques lourdes.

## Machine Learning-Based Online Coverage Estimator (MLOE): Advancing Mobile Network Planning and Optimization (2023)

Méthode qui permet de connaître l'endroit le plus optimisé pour installer une antenne pour ensuite éviter les zone blanche innatendue. Bien avant l'IoT, des équations empiriques permettaient de modéliser les emplacements mais avec le nombre grandissant d'appareil, ces équations ne sont plus précise. Les chercheurs on alors développé une model dynamique qui permet d'estimer la force des signaux à un endroit précis. Cette méthode ce repose sur 7 variables dont la hauteur de l'antenne ainsi que son altitude. Cette méthode s'appui sur l'algorithme "Random Forest" qui permet de créer différents arbres de prédiction pui les combine pour avoir le résultat le plus précis.
Cette solution est disponible en ligne.

- **1. Le contexte : La fin des modèles de planification à l'ancienne**
Historiquement, pour planifier le déploiement de leurs antennes, les opérateurs de télécommunications utilisent des "modèles empiriques" (comme Okumura-Hata ou COST-231). Ces modèles reposent sur des équations mathématiques figées créées il y a des décennies.Le problème : Avec l'arrivée de la 5G, de la 6G et de l'Internet des Objets (IoT) massif, les environnements radio deviennent beaucoup trop complexes pour ces vieilles équations. Elles manquent de précision et ne s'adaptent pas aux changements urbains.L'impulsion de l'industrie : L'organisme mondial qui standardise les réseaux mobiles (le 3GPP), à travers sa Release 18, a officiellement acté que l'Intelligence Artificielle devait désormais être intégrée au cœur de la conception et de l'optimisation des futurs réseaux cellulaires. Cet article s'inscrit exactement dans cette directive.

- **2. La solution proposée : L'outil MLOE**
Les chercheurs n'ont pas seulement écrit une équation, ils ont conçu une véritable architecture logicielle nommée MLOE (Machine Learning-Based Online Coverage Estimator - Estimateur de couverture en ligne basé sur le ML).L'objectif de MLOE est de remplacer les vieux simulateurs par un outil intelligent, capable d'apprendre des données réelles du réseau pour prédire avec précision la force du signal (le paramètre RSRP - Reference Signal Received Power).

- **3. Comment ça marche ? (Le cœur algorithmique)**
Sélection des données (Les 7 caractéristiques) : Pour prédire le signal, l'algorithme n'a pas besoin d'une infinité de paramètres. L'étude a isolé 7 variables clés d'entrée (les features), telles que la distance entre l'utilisateur et l'antenne, la fréquence utilisée, les hauteurs d'antennes, ou encore le type d'environnement (urbain, rural, etc.).L'algorithme de la "Forêt Aléatoire" (Random Forest) : Après avoir testé plusieurs méthodes d'apprentissage supervisé, les auteurs ont choisi le modèle Random Forest. Il s'agit d'un algorithme qui crée une multitude d'"arbres de décision" basés sur les données historiques. En combinant les prédictions de tous ces arbres, il obtient une estimation finale du signal qui est extrêmement robuste et peu sensible aux erreurs aberrantes.Un fonctionnement "En ligne" (Cloud) : C'est la grande originalité de l'article. Plutôt que de rester un code sur l'ordinateur d'un chercheur, MLOE a été packagé sous forme de composant logiciel hébergé sur le Cloud (via le serveur d'applications Web de MATLAB). Cela signifie qu'un ingénieur sur le terrain peut s'y connecter via une interface web, envoyer de nouvelles mesures de terrain, et le modèle se ré-entraîne et s'affine "en ligne" et en continu.

- **4. Les résultats obtenus**
L'algorithme a été testé sur des bases de données réelles massives.Précision mathématique : Il a atteint un $R^2$ (coefficient de détermination) de 0,93 (ce qui signifie que le modèle explique 93% des variations du signal, un score excellent) et une marge d'erreur moyenne (RMSE) de seulement 2,65 dB. En comparaison, les modèles empiriques classiques font souvent des erreurs de 7 à 10 dB.Impact pour les opérateurs : En utilisant MLOE, un opérateur peut planifier le déploiement de ses antennes 5G ou de ses capteurs IoT de manière beaucoup plus fine. Cela évite les "zones blanches" imprévues et empêche la sur-installation coûteuse et inutile d'antennes (optimisation des coûts de déploiement et d'énergie).

Limites (Le "Research Gap" pour justifier ton projet) :
Cette étude est très performante, mais elle est conçue pour des infrastructures lourdes (réseaux 4G/5G cellulaires) où l'énergie et la puissance de calcul ne sont pas un problème. Le modèle tourne sur un serveur distant (Cloud/Web App).
Pour ton article : Tu peux souligner que pour des réseaux IoT (comme LoRaWAN), il est impossible d'appliquer des méthodes nécessitant une telle infrastructure ou des serveurs distants en permanence. Ton projet se démarque car il utilise le Machine Learning (également Random Forest) mais appliqué aux signaux RSSI de réseaux LoRa basse consommation, et surtout, l'intelligence artificielle est exécutée localement (Edge Computing) sur un micro-ordinateur embarqué (Jetson Nano) plutôt que sur un gros serveur cloud. Cela répond directement aux contraintes de connectivité et d'énergie des réseaux de capteurs (WSN).

## Mobile Network Coverage Prediction Based on Supervised Machine Learning Algorithms (2022)

Ici on compare les différents modèles d'IA qui permetten d'estimer la couverture réseau et de créer alors un nouveau réseau. On compare plusieurs modèle mais la conclusion est qu'il 

- **1. Le contexte et le problème à résoudre**
Depuis quelques années, l'utilisation de l'Apprentissage Automatique (Machine Learning - ML) pour prédire la couverture réseau est devenue très populaire.Le problème : Il existe des dizaines d'algorithmes de ML différents. Un ingénieur télécom qui souhaite moderniser son réseau se retrouve face à une "jungle" de modèles d'IA sans savoir lequel choisir. Faut-il utiliser un réseau de neurones complexes ? Une simple régression ?L'objectif de cet article est donc de faire un grand "benchmark" (un test comparatif rigoureux) pour évaluer quel algorithme est le plus adapté pour prédire la perte de signal entre deux antennes terrestres (ce qu'on appelle les communications Ground-to-Ground ou G2G).

- **2. La méthodologie : La bataille des algorithmes**
Les chercheurs ont rassemblé un grand jeu de données contenant des mesures de signal radio sur différentes bandes de fréquences, distances et hauteurs d'antennes. Ils ont ensuite entraîné et testé 6 grandes familles d'algorithmes (comprenant plus de 20 variantes au total) :Régression Linéaire (LR) : L'approche statistique la plus simple.Arbres de Régression (RT) : Un algorithme qui fonctionne par une série de règles de décision (si la distance > X, alors le signal = Y).Machines à Vecteurs de Support (SVM) : Très connues pour la classification, adaptées ici pour prédire une valeur continue.Réseaux de Neurones Artificiels (ANN) : L'IA "classique" inspirée du cerveau humain.Processus Gaussien (GPR - Gaussian Process Regression) : Une méthode probabiliste très puissante en mathématiques pures.Ensembles d'Arbres (ET - Ensembles of Trees) : Une méthode qui combine des centaines d'arbres de décision (comme l'algorithme de la Forêt Aléatoire mentionné dans le 3ème article) pour moyenner leurs résultats.

- **3. Les critères d'évaluation**
Pour déterminer le gagnant, les auteurs n'ont pas seulement regardé la précision. Ils ont utilisé une double évaluation, indispensable dans le monde industriel :La précision statistique : L'algorithme se trompe-t-il de beaucoup de décibels (dB) ? (Mesuré via l'erreur RMSE et le score $R^2$).L'efficacité temporelle (La vitesse) : Combien de temps l'algorithme met-il à "apprendre" (temps d'entraînement) et combien de temps met-il à calculer une nouvelle prédiction ?
- **4. Les résultats : La nuance entre Théorie et Pratique**
C'est ici que l'article devient très intéressant, car il révèle un vrai dilemme d'ingénieur :Le grand gagnant théorique (La précision pure) : L'algorithme GPR (Processus Gaussien) remporte la palme de la précision mathématique. Il fait le moins d'erreurs. Cependant, il est extrêmement lourd et lent. Sur un réseau réel où il faut calculer des millions de points, il prendrait beaucoup trop de temps et consommerait trop de ressources informatiques.Le grand gagnant pratique (Le choix recommandé) : La famille des Ensembles d'Arbres (ET) (qui inclut la Forêt Aléatoire). Cet algorithme offre une précision presque identique au GPR (l'écart d'erreur est négligeable), mais il est infiniment plus rapide à s'entraîner et à générer des prédictions.

- **En résumé**
Cet article est un guide d'aide à la décision. Sa conclusion forte pour l'industrie est la suivante : « Ne vous laissez pas aveugler par la perfection mathématique des Processus Gaussiens ou la complexité des Réseaux de Neurones. Pour planifier un réseau mobile de manière rapide, précise et sur plusieurs fréquences différentes, la méthode des Ensembles d'Arbres (ET / Random Forest) est le meilleur outil à déployer. »(C'est d'ailleurs exactement la conclusion que les auteurs du 3ème article ont appliquée en choisissant la Forêt Aléatoire pour leur outil en ligne !).

Limites (Le "Research Gap" pour justifier ton projet) :
L'étude reste purement axée sur les réseaux cellulaires haut débit (4G/LTE), qui bénéficient d'infrastructures lourdes et n'ont pas de réelles contraintes énergétiques pour collecter et traiter la donnée.
Pour ton article : Ce papier est une pépite pour toi ! Il te permet de justifier scientifiquement ton propre choix d'algorithme. Tu pourras argumenter ainsi dans ta section : "Des études comparatives exhaustives ont prouvé que le Random Forest offre le meilleur compromis entre vitesse et précision pour la prédiction de couverture. Toutefois, ces recherches se limitent aux réseaux cellulaires classiques. Notre projet comble cette lacune en transposant l'efficacité du Random Forest à la localisation et la prédiction dans des réseaux IoT très basse consommation (LoRa) via la mesure du RSSI. Surtout, nous prouvons que cette IA peut s'exécuter localement sur du matériel à ressources très limitées (Jetson Nano) grâce au Edge Computing."

## Empowering Extreme Communication: Propagation Characterization of a LoRa-Based Internet of Things Network Using Hybrid Machine Learning (2024)

Cet article essai de démontrer qu'il est possible de déployer des réseaux IoT dans des milieux extrême tel que la jungle ou les lacs, des environnements peu propice au propagations des ondes radios car l'humidité et l'eau sont des réels barrière. Pour cela les chercheur essaie un modèle de prediction Hybride. C'est à dire qu'il prédise la couverture avec les formules connus mais solicite une IA pour corriger et prédire les couverture. Avec ça ils ont configuré 2 set-up. Un et-up avec une antenne à 25m de haut (cime des arbres) et une autre à 120m, largement au dessus de la forêt. Ils se sont rendu compte que l'antenne placée à 120m de haut avait une meilleur couverture (6.4 Km).

- **1. Le contexte : Le cauchemar des ondes radio**
L'article se concentre sur une technologie spécifique appelée LoRa (Long Range). C'est un réseau conçu pour l'Internet des Objets (IoT), qui permet à de petits capteurs fonctionnant sur pile de communiquer sur de longues distances. C'est idéal pour surveiller l'environnement (qualité de l'eau, détection d'incendies, braconnage).
Le problème ("Extreme Communication") : Les ondes radio détestent deux choses : l'eau (qui fait ricocher et s'évanouir le signal) et la végétation dense (dont l'humidité absorbe littéralement les ondes). Les formules mathématiques traditionnelles pour calculer la portée d'une antenne ont été conçues pour les villes ou les plaines dégagées. Dans une jungle tropicale avec des lacs, ces vieilles formules sont totalement aveugles et fausses.

- **2. Une campagne de mesures inédite (Le Lac Chini)**
Pour comprendre comment le signal se comporte réellement dans ces conditions extrêmes, les chercheurs se sont rendus au Lac Chini, en Malaisie (une réserve de biosphère très dense).
Au lieu des habituels "Drive-tests" (en voiture), ils ont inventé le "Boat Drive-test" : ils ont placé des capteurs LoRa sur des bateaux naviguant sur le lac, tout en effectuant des mesures à pied à travers l'épaisse forêt tropicale environnante.
Ils ont également voulu tester l'impact de l'infrastructure en plaçant l'antenne de réception (la "Gateway") à deux hauteurs très différentes : 25 mètres (juste au niveau de la cime des arbres) et 120 mètres (sur un grand pylône télécom dominant la canopée).

 - **3. L'intelligence artificielle "Hybride" à la rescousse**
Pour donner un sens à ces données très complexes (où le signal fluctue énormément à cause des arbres et des reflets de l'eau), ils ont utilisé le Machine Learning Hybride.
Plutôt que de choisir entre un modèle physique classique ou un modèle d'IA pur (comme vu dans les articles précédents), l'approche hybride combine les deux.
L'algorithme prend en compte les lois de la physique de base, mais utilise l'Intelligence Artificielle pour "apprendre" et corriger les erreurs causées spécifiquement par l'absorption des feuilles, les collines et l'évaporation de l'eau.

- **4. Les résultats et l'impact pour l'industrie**
Le triomphe de l'IA : Les modèles classiques d'ingénierie se trompaient lourdement sur la puissance du signal. Le modèle d'IA hybride, en revanche, a réussi à prédire presque parfaitement la couverture radio, prouvant que seule l'IA peut s'adapter à une topographie aussi chaotique.
L'importance cruciale de la hauteur : L'étude a prouvé qu'à 25 mètres de haut, l'antenne était "étouffée" par la végétation, limitant drastiquement la portée. En revanche, en la plaçant à 120 mètres, le signal parvient à "surfer" au-dessus de la canopée, offrant une couverture réseau robuste s'étendant à plus de 6,5 kilomètres.

- **En résumé**
Cet article prouve qu'il est tout à fait possible de déployer des réseaux de capteurs (IoT) performants dans les endroits les plus hostiles et inaccessibles de la planète pour protéger l'environnement. Mais pour que cela fonctionne, les ingénieurs ne peuvent plus se fier aux vieux manuels : ils doivent absolument coupler des antennes très hautes avec des prédictions basées sur l'Intelligence Artificielle.

Limites (Le "Research Gap" pour justifier ton projet) :
Bien que cette étude soit très avancée, elle se limite exclusivement à la prédiction de l'atténuation du signal (Path Loss) pour estimer la couverture du réseau. L'objectif n'est pas de localiser physiquement un capteur (trouver ses coordonnées X, Y). De plus, ces modèles complexes sont conçus pour de la planification de réseau hors-ligne.
Pour ton article : Ce papier est ton arme secrète pour justifier tes choix techniques. Tu peux écrire : « De très récentes recherches (Alobaidy et al., 2024) ont incontestablement prouvé que les algorithmes basés sur les arbres (Random Forest) sont les plus performants pour modéliser les fluctuations complexes du signal LoRa (RSSI) face aux obstacles, offrant le meilleur équilibre entre précision et vitesse de calcul, et surpassant même les réseaux de neurones. Notre projet s'appuie sur cette validation scientifique du Random Forest pour franchir l'étape suivante : nous ne l'utilisons plus seulement pour prédire théoriquement la couverture, mais nous le couplons à la multilatération (MTL) pour accomplir une localisation active. De plus, notre implémentation sur une Jetson Nano prouve qu'une telle intelligence prédictive peut être déployée de manière autonome et frugale sur un nœud Edge (Edge Computing), comblant ainsi le besoin en localisation temps-réel de l'IoT. »

## Wireless Transmissions, Propagation and Channel Modelling for IoT Technologies: Applications and Challenges (2022)

Cet article fais l'inventaire des différentes ondes et leur comportement dans certain milieu

- **1. Le contexte : Le "Far West" de l'Internet des Objets (IoT)**
Aujourd'hui, l'IoT est partout : montres connectées, capteurs agricoles, compteurs d'eau intelligents, usines automatisées (Smart Cities, e-Health, Industry 4.0).
Pour faire communiquer tous ces objets, il existe une multitude de technologies différentes : certaines à très courte portée (Bluetooth, Zigbee, Wi-Fi) et d'autres à très longue portée (LoRa, Sigfox, NB-IoT).
Le problème : Un ingénieur qui veut déployer un réseau cellulaire classique (4G/5G) sait comment faire. Mais pour l'IoT, les scénarios sont tellement variés et extrêmes qu'il n'existait pas de manuel unique expliquant comment les ondes radio se comportent pour chaque technologie et chaque milieu. Cet article a été écrit pour combler ce vide.

- **2. Le casse-tête spécifique des capteurs IoT**
L'article met en évidence pourquoi on ne peut pas simplement réutiliser les équations mathématiques des réseaux mobiles classiques (les téléphones) pour l'IoT. L'IoT impose des défis physiques uniques :
La position des antennes : Contrairement à un smartphone situé à 1,50 m du sol, un capteur IoT peut être enterré sous terre (agriculture), collé sur un tuyau en métal dans une cave (compteur d'eau), ou même implanté à l'intérieur du corps humain (pacemaker connecté). Ces positions inhabituelles détruisent les ondes radio de manière très spécifique.
La taille et l'énergie : Les capteurs IoT sont minuscules et fonctionnent sur pile pendant 10 ans. Leurs petites antennes ont une puissance d'émission extrêmement faible, ce qui rend le signal très vulnérable aux obstacles.

- **3. Le cœur de l'article : Un catalogue géant des modèles de propagation**
Les auteurs ont épluché des centaines de publications scientifiques pour dresser un inventaire complet. Ils ont classé la façon dont les ondes se propagent selon la distance :

Les réseaux corporels (WBAN - Wireless Body Area Networks) : Comment modéliser un signal qui doit traverser la peau, le gras et les muscles sans être totalement absorbé (cas des applications médicales).

Les réseaux locaux et personnels (WLAN / WPAN) : Comment les ondes (comme le Wi-Fi ou le Bluetooth) rebondissent à l'intérieur des maisons intelligentes (Smart Homes) sur les murs, les meubles et les personnes en mouvement.

Les réseaux longue portée (LPWAN) : L'article détaille les modèles mathématiques pour les technologies comme LoRa ou NB-IoT, qui doivent couvrir des villes entières ou de vastes zones rurales, en analysant l'impact de la météo, des bâtiments et du relief.

4. Quel est l'intérêt d'un tel article ?
Pour comprendre l'utilité de ce type de publication, imaginez-le comme la carte d'état-major de l'ingénierie des télécoms.
Il explique les avantages et les défauts de chaque grande famille de modèles (les modèles empiriques basés sur l'observation, les modèles déterministes basés sur la géométrie 3D, et les modèles stochastiques basés sur les probabilités).
Il souligne également les défis de demain : comment assurer la sécurité du signal IoT, comment gérer les interférences quand des milliards d'objets parleront en même temps, et comment localiser un objet avec précision sans utiliser de GPS (trop gourmand en batterie).

En résumé
Alors que les articles 1 à 5 sont les "outils" (ils inventent de nouveaux marteaux ou tournevis à l'aide de l'Intelligence Artificielle), ce 6ème article est la "boîte à outils théorique". C'est le point de départ incontournable : tout chercheur ou ingénieur qui souhaite créer une Intelligence Artificielle pour optimiser un réseau IoT (comme l'ont fait les auteurs de l'article 5 au Lac Chini) commence par lire ce genre de synthèse pour comprendre la physique des ondes qu'il va manipuler.

Limites (Le "Research Gap" pour justifier ton projet) :
La revue souligne qu'il existe encore d'énormes lacunes dans la modélisation des canaux pour LoRa : la majorité des études se contentent d'utiliser des modèles trop simples (comme LNSPL) ou se limitent à des environnements urbains basiques sans tenir compte des conditions réelles complexes. Surtout, les auteurs concluent que l'avenir réside dans le développement de techniques de prédiction hybrides combinant le Machine Learning avec des données réelles, mais que ce domaine en est encore à ses balbutiements.
Pour ton article : C'est l'argument ultime pour introduire la section "Proposed Method". Tu peux écrire : « De récentes revues de littérature exhaustives ont souligné l'imprécision des modèles mathématiques classiques pour estimer le signal (RSSI) et la localisation dans les réseaux LoRa, appelant fermement à l'intégration de méthodes basées sur le Machine Learning. Notre étude répond directement à ce besoin (Research Gap) en proposant un modèle Random Forest basé sur la multilatération (MTL) du RSSI. Contrairement aux approches limitées au Cloud, notre système embarque cette intelligence artificelle directement sur un nœud Edge (Jetson Nano), alliant ainsi précision algorithmique et autonomie matérielle. »

## Idée a prendre

Dans l'article 6 nous parlons de smart City et de l'automatisation de certain domaine. Ici on prend l'exemple de l'extinction de l'éclairage urbain enfin d'enssoleillement visant ainsi à réduire les émissions.
l'IoT peut être assimilé à Emergency IoT (EIoT) donc detecteur d'alarme.
Les dispositifs IoT disposent d'une faible capacité d'alimentation, souvant sur batterie.

On peut accéder à la localisation des appareils avec the position can be obtained using Global Navigation Satellite Systems (GNSS), such as the Global Positioning System (GPS), si cela en sont pourvu. Pas fiable dans environnement indoor. C'est un challenge an IoT. On peut sa'ppuyer sur des élément comme la phase ou l'angle d'arrivé de l'onde

Les canaux sans fils doivent être bien choi car le moindre relief peut affaiblir le sognal et le rendre indetectable.
Le model d'okomura hata ne prend pas en compte les reliefs