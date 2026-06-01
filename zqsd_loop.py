"""
.gg/zmn5 — répète en boucle les touches Z, Q, S, D tant que c'est activé.

- Interface minimale (tkinter).
- Délai réglable en millisecondes (durée pendant laquelle chaque touche est maintenue).
- Touche raccourci configurable pour démarrer / arrêter la boucle.

Pour fonctionner DANS LES JEUX (DirectInput / Raw Input), on envoie de vrais
scan codes matériels via l'API Windows SendInput, et non de simples frappes
virtuelles. Sur AZERTY, les touches ZQSD occupent la même position physique que
WASD : on envoie donc les scan codes de ces positions physiques.

Dépendance : pynput (pour écouter la touche raccourci).
"""

import sys
import threading
import time
import tkinter as tk

from pynput.keyboard import Controller, Key, KeyCode, Listener


# Nom affiché de l'application.
APP_NAME = ".gg/zmn5"

IS_WINDOWS = sys.platform == "win32"

# Touche raccourci par défaut pour activer / désactiver la boucle.
DEFAULT_TOGGLE_KEY = Key.f8

# Séquence répétée : (label affiché, scan code matériel set 1).
# Les scan codes correspondent aux positions physiques de WASD,
# c'est-à-dire les touches Z, Q, S, D d'un clavier AZERTY.
SEQUENCE = [
    ("Z", 0x11),  # position physique du W
    ("Q", 0x1E),  # position physique du A
    ("S", 0x1F),
    ("D", 0x20),
]


# ---------------------------------------------------------------------------
# Envoi de frappes au niveau matériel (scan codes) — fonctionne dans les jeux.
# ---------------------------------------------------------------------------
if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    ULONG_PTR = ctypes.POINTER(ctypes.c_ulong)

    class _MOUSEINPUT(ctypes.Structure):
        _fields_ = (
            ("dx", wintypes.LONG),
            ("dy", wintypes.LONG),
            ("mouseData", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        )

    class _KEYBDINPUT(ctypes.Structure):
        _fields_ = (
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ULONG_PTR),
        )

    class _HARDWAREINPUT(ctypes.Structure):
        _fields_ = (
            ("uMsg", wintypes.DWORD),
            ("wParamL", wintypes.WORD),
            ("wParamH", wintypes.WORD),
        )

    class _INPUTUNION(ctypes.Union):
        _fields_ = (("mi", _MOUSEINPUT), ("ki", _KEYBDINPUT), ("hi", _HARDWAREINPUT))

    class _INPUT(ctypes.Structure):
        _fields_ = (("type", wintypes.DWORD), ("u", _INPUTUNION))

    _INPUT_KEYBOARD = 1
    _KEYEVENTF_SCANCODE = 0x0008
    _KEYEVENTF_KEYUP = 0x0002

    _SendInput = ctypes.windll.user32.SendInput

    def _send_scancode(scan, keyup):
        flags = _KEYEVENTF_SCANCODE | (_KEYEVENTF_KEYUP if keyup else 0)
        ki = _KEYBDINPUT(wVk=0, wScan=scan, dwFlags=flags, time=0, dwExtraInfo=None)
        inp = _INPUT(type=_INPUT_KEYBOARD, u=_INPUTUNION(ki=ki))
        _SendInput(1, ctypes.byref(inp), ctypes.sizeof(inp))

    def key_down(scan):
        _send_scancode(scan, keyup=False)

    def key_up(scan):
        _send_scancode(scan, keyup=True)

else:
    # Repli (développement hors Windows) : frappes virtuelles via pynput.
    # Ne fonctionnera PAS dans la plupart des jeux, mais suffit pour tester l'UI.
    _kb = Controller()
    _SCAN_TO_CHAR = {0x11: "z", 0x1E: "q", 0x1F: "s", 0x20: "d"}

    def key_down(scan):
        _kb.press(_SCAN_TO_CHAR.get(scan, "z"))

    def key_up(scan):
        _kb.release(_SCAN_TO_CHAR.get(scan, "z"))


def key_label(key):
    """Renvoie un nom lisible pour une touche pynput."""
    if isinstance(key, KeyCode) and key.char is not None:
        return key.char.upper()
    if isinstance(key, Key):
        return key.name.upper()
    return str(key)


class ZQSDLoop:
    def __init__(self, root):
        self.root = root

        self.running = False              # boucle active ?
        self.delay_ms = 100               # durée de maintien de chaque touche
        self.worker = None                # thread qui envoie les frappes
        self.toggle_key = DEFAULT_TOGGLE_KEY
        self.capturing = False            # en train de capturer une nouvelle touche ?

        self._build_ui()

        # Écoute le clavier en arrière-plan pour le raccourci.
        self.listener = Listener(on_press=self._on_key)
        self.listener.daemon = True
        self.listener.start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ----- Interface ---------------------------------------------------
    def _build_ui(self):
        self.root.title(APP_NAME)
        self.root.resizable(False, False)

        frame = tk.Frame(self.root, padx=16, pady=16)
        frame.pack()

        tk.Label(
            frame, text=APP_NAME, font=("TkDefaultFont", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        tk.Label(frame, text="Délai (ms) :").grid(row=1, column=0, sticky="w")
        self.delay_var = tk.StringVar(value=str(self.delay_ms))
        tk.Entry(frame, textvariable=self.delay_var, width=8).grid(
            row=1, column=1, padx=(8, 0), sticky="e"
        )

        tk.Label(frame, text="Touche :").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.key_button = tk.Button(
            frame, text=key_label(self.toggle_key), command=self.capture_key
        )
        self.key_button.grid(row=2, column=1, padx=(8, 0), sticky="e", pady=(8, 0))

        self.status = tk.Label(
            frame, text="Arrêté", fg="red", font=("TkDefaultFont", 12, "bold")
        )
        self.status.grid(row=3, column=0, columnspan=2, pady=(12, 8))

        self.button = tk.Button(frame, text="Démarrer", command=self.toggle)
        self.button.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.hint = tk.Label(
            frame, text=self._hint_text(), fg="gray", font=("TkDefaultFont", 8)
        )
        self.hint.grid(row=5, column=0, columnspan=2, pady=(8, 0))

        if not IS_WINDOWS:
            tk.Label(
                frame,
                text="(Hors Windows : mode test, inactif dans les jeux)",
                fg="orange",
                font=("TkDefaultFont", 8),
            ).grid(row=6, column=0, columnspan=2, pady=(4, 0))

    def _hint_text(self):
        return f"{key_label(self.toggle_key)} démarre / arrête la boucle"

    # ----- Logique -----------------------------------------------------
    def _read_delay(self):
        try:
            value = int(self.delay_var.get())
            return max(1, value)
        except ValueError:
            return self.delay_ms

    def capture_key(self):
        """Active la capture : la prochaine touche pressée devient le raccourci."""
        self.capturing = True
        self.key_button.config(text="Appuyez...")

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def start(self):
        if self.running:
            return
        self.delay_ms = self._read_delay()
        self.running = True
        self.worker = threading.Thread(target=self._loop, daemon=True)
        self.worker.start()
        self._update_ui()

    def stop(self):
        self.running = False
        self._update_ui()

    def _loop(self):
        delay = self.delay_ms / 1000.0
        held = None
        try:
            while self.running:
                for _, scan in SEQUENCE:
                    if not self.running:
                        break
                    key_down(scan)
                    held = scan
                    time.sleep(delay)
                    key_up(scan)
                    held = None
        finally:
            # Sécurité : on relâche toute touche restée enfoncée.
            if held is not None:
                key_up(held)

    def _on_key(self, key):
        if self.capturing:
            self.root.after(0, lambda: self._set_toggle_key(key))
        elif key == self.toggle_key:
            self.root.after(0, self.toggle)

    def _set_toggle_key(self, key):
        self.toggle_key = key
        self.capturing = False
        self.key_button.config(text=key_label(key))
        self.hint.config(text=self._hint_text())

    def _update_ui(self):
        if self.running:
            self.status.config(text="En cours", fg="green")
            self.button.config(text="Arrêter")
        else:
            self.status.config(text="Arrêté", fg="red")
            self.button.config(text="Démarrer")

    def _on_close(self):
        self.running = False
        self.listener.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    ZQSDLoop(root)
    root.mainloop()


if __name__ == "__main__":
    main()
