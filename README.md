# .gg/zmn5

Petite appli qui répète en boucle les touches **Z, Q, S, D** tant qu'elle est
activée. Idéale pour les jeux : elle envoie de vraies frappes clavier au système.

## Fonctionnement

- Interface minimale (tkinter).
- **Délai réglable en millisecondes** : durée pendant laquelle chaque touche
  est maintenue avant de passer à la suivante.
- **Touche raccourci configurable** pour démarrer / arrêter la boucle
  (F8 par défaut). Clique sur le bouton de la touche, puis appuie sur la
  nouvelle touche souhaitée.

## Compatibilité avec les jeux

La plupart des jeux ignorent les frappes "virtuelles" classiques : ils lisent
le clavier au niveau matériel (DirectInput / Raw Input). Cette appli envoie donc
de vrais **scan codes matériels** via l'API Windows `SendInput`, ce qui revient à
appuyer réellement sur les touches.

- Sur **AZERTY**, les touches `Z, Q, S, D` occupent la même position physique que
  `W, A, S, D` : l'appli envoie ces positions physiques, donc le jeu reçoit bien
  tes touches de déplacement.
- **Lancer en administrateur** : si le jeu tourne en administrateur, l'appli doit
  l'être aussi pour que les frappes l'atteignent. L'exe est compilé avec une
  demande d'élévation automatique (UAC). Sinon : clic droit → *Exécuter en tant
  qu'administrateur*.
- ⚠️ **Jeux avec anti-triche** (BattlEye, EAC, Vanguard…) : l'injection d'entrée
  est généralement détectée et/ou bloquée. N'utilise cet outil que sur des jeux
  qui l'autorisent (solo, fermes, jeux sans anti-triche).

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
3. En bas, télécharge l'artefact **`zmn5-windows`** → il contient
   `zmn5.exe`.

Astuce : pousse un tag `vX.Y` (ex. `git tag v1.0 && git push origin v1.0`)
pour attacher directement l'exe à une *Release* GitHub.

### Option B — compiler soi-même sur un PC Windows

```bash
pip install -r requirements.txt pyinstaller
pyinstaller --onefile --windowed --name "zmn5" zqsd_loop.py
```

Le fichier est généré dans `dist/zmn5.exe`.

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
