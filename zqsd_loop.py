"""
.gg/zmn5 — répète en boucle les touches Z, Q, S, D tant que c'est activé.

- Interface minimale (tkinter).
- Délai réglable en millisecondes entre chaque frappe.
- Touche raccourci configurable pour démarrer / arrêter la boucle.

Dépendance : pynput (voir requirements.txt).
"""

import threading
import time
import tkinter as tk

from pynput.keyboard import Controller, Key, KeyCode, Listener


# Nom affiché de l'application.
APP_NAME = ".gg/zmn5"

# Les touches répétées en boucle, dans l'ordre.
SEQUENCE = ["z", "q", "s", "d"]

# Touche raccourci par défaut pour activer / désactiver la boucle.
DEFAULT_TOGGLE_KEY = Key.f8


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
        self.keyboard = Controller()

        self.running = False              # boucle active ?
        self.delay_ms = 100               # délai entre deux frappes
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

        # Titre / nom de l'appli.
        tk.Label(
            frame, text=APP_NAME, font=("TkDefaultFont", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        tk.Label(frame, text="Délai (ms) :").grid(row=1, column=0, sticky="w")
        self.delay_var = tk.StringVar(value=str(self.delay_ms))
        tk.Entry(frame, textvariable=self.delay_var, width=8).grid(
            row=1, column=1, padx=(8, 0), sticky="e"
        )

        # Ligne pour changer la touche d'activation.
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
            frame,
            text=self._hint_text(),
            fg="gray",
            font=("TkDefaultFont", 8),
        )
        self.hint.grid(row=5, column=0, columnspan=2, pady=(8, 0))

    def _hint_text(self):
        return f"{key_label(self.toggle_key)} démarre / arrête la boucle"

    # ----- Logique -----------------------------------------------------
    def _read_delay(self):
        try:
            value = int(self.delay_var.get())
            return max(1, value)  # au moins 1 ms pour ne pas saturer le CPU
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
        while self.running:
            for key in SEQUENCE:
                if not self.running:
                    break
                self.keyboard.press(key)
                self.keyboard.release(key)
                time.sleep(delay)

    def _on_key(self, key):
        # On revient sur le thread tkinter pour manipuler l'UI sans risque.
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
