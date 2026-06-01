# ZQSD Loop

Petite appli qui répète en boucle les touches **Z, Q, S, D** tant qu'elle est
activée. Idéale pour les jeux : elle envoie de vraies frappes clavier au système.

## Fonctionnement

- Interface minimale (tkinter).
- **Délai réglable en millisecondes** entre chaque frappe.
- Touche raccourci **F8** pour démarrer / arrêter la boucle (ou le bouton).

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python zqsd_loop.py
```

1. Règle le délai en ms (par défaut 100).
2. Appuie sur **F8** (ou clique sur *Démarrer*) pour lancer la boucle.
3. Appuie de nouveau sur **F8** pour l'arrêter.

## Notes par plateforme

- **Windows** : fonctionne directement.
- **macOS** : autoriser l'app dans *Réglages → Confidentialité et sécurité →
  Accessibilité* (et *Surveillance de la saisie*) pour que les frappes soient
  envoyées.
- **Linux** : nécessite un serveur X (X11). Sous Wayland, la simulation de
  frappes peut être limitée.

## Personnalisation

Dans `zqsd_loop.py` :

- `SEQUENCE` : la liste des touches répétées (par défaut `["z", "q", "s", "d"]`).
- `TOGGLE_KEY` : la touche raccourci (par défaut `Key.f8`).
