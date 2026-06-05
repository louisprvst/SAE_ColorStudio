Color Studio
=============

Courte présentation
--------------------
Color Studio est une application PyQt6 pour visualiser et tester des configurations d'éclairage et de post-traitement sur des images (scène de lumières, exposition automatique, saturation, etc.).

Prérequis
---------
- Python 3.12+
- Pip
- Les dépendances listées dans `requirements.txt` (PyQt6, numpy, scikit-image, imageio, moderngl...)

Installation
------------
1. (Optionnel) Crée un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Installe les dépendances :

```bash
python3 -m pip install -r requirements.txt
```

Lancer l'application
--------------------
Depuis la racine du projet :

```bash
python3 colorStudioApp.py
```

Au démarrage l'application ouvre une boîte de dialogue pour choisir un fichier XML de configuration de scène. Si tu ne choisis rien, le fichier par défaut `xml-2019-6-7-22-47-1.xml` sera chargé.

Utilisation rapide (guide)
-------------------------
- Panneau de gauche (Contrôles) :
	- `Load` / `Save` : charger ou sauvegarder une configuration XML.
	- Pour chaque lumière :
		- Boutons `EV -` / `EV +` : diminuer/augmenter l'exposition de la lumière active.
		- `Color` : ouvre le sélecteur de couleur (ou utilise la roue chromatique) pour définir la couleur de la source.
		- Curseur : position de la source (index d'image).
	- `Automatic Exposure` : bascule AE On/Off et commandes EV quand AE est désactivé.
	- `Saturation` : sliders pour régler la saturation linéaire et gamma.

- Zone centrale : rendu principal de la scène (aperçu RGB).
- Colonne droite : visualisation 3D des points de couleur et roue chromatique — utiliser la roue pour sélectionner une couleur et voir son effet.

Modifier une scène
------------------
- Les fichiers de scène sont au format XML (exemples fournis : `xml-*.xml`). Tu peux modifier ces XML manuellement ou via l'UI (Load / Save).
- Pour ajouter/éditer une lumière : modifier l'entrée correspondante dans le XML (chemins d'images, exposition, couleur, index).

Tests
-----
Pour exécuter la suite de tests unitaires :

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Il existe aussi un fichier de tests à la racine `test_colorStudioModel.py`.