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

## Obtenir le `.exe` Windows

### Option A — build automatique (GitHub Actions, rien à installer)

Un workflow (`.github/workflows/build-exe.yml`) compile le `.exe` sur une
machine Windows à chaque push de la branche.

1. Sur GitHub, onglet **Actions** → workflow **Build Windows EXE**.
2. Ouvre le dernier run (ou lance-le via **Run workflow**).
3. En bas, télécharge l'artefact **`ZQSD-Loop-windows`** → il contient
   `ZQSD-Loop.exe`.

Astuce : pousse un tag `vX.Y` (ex. `git tag v1.0 && git push origin v1.0`)
pour attacher directement l'exe à une *Release* GitHub.

### Option B — compiler soi-même sur un PC Windows

```bash
pip install -r requirements.txt pyinstaller
pyinstaller --onefile --windowed --name "ZQSD-Loop" zqsd_loop.py
```

Le fichier est généré dans `dist/ZQSD-Loop.exe`.

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
