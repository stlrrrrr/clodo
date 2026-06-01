"""
ZQSD Loop — répète en boucle les touches Z, Q, S, D tant que c'est activé.

- Interface minimale (tkinter).
- Délai réglable en millisecondes entre chaque frappe.
- Une touche raccourci (F8 par défaut) pour démarrer / arrêter la boucle.

Dépendance : pynput (voir requirements.txt).
"""

import threading
import time
import tkinter as tk

from pynput.keyboard import Controller, Key, Listener


# Les touches répétées en boucle, dans l'ordre.
SEQUENCE = ["z", "q", "s", "d"]

# Touche raccourci pour activer / désactiver la boucle.
TOGGLE_KEY = Key.f8


class ZQSDLoop:
    def __init__(self, root):
        self.root = root
        self.keyboard = Controller()

        self.running = False          # boucle active ?
        self.delay_ms = 100           # délai entre deux frappes
        self.worker = None            # thread qui envoie les frappes

        self._build_ui()

        # Écoute le clavier en arrière-plan pour le raccourci F8.
        self.listener = Listener(on_press=self._on_key)
        self.listener.daemon = True
        self.listener.start()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ----- Interface ---------------------------------------------------
    def _build_ui(self):
        self.root.title("ZQSD Loop")
        self.root.resizable(False, False)

        frame = tk.Frame(self.root, padx=16, pady=16)
        frame.pack()

        tk.Label(frame, text="Délai (ms) :").grid(row=0, column=0, sticky="w")
        self.delay_var = tk.StringVar(value=str(self.delay_ms))
        tk.Entry(frame, textvariable=self.delay_var, width=8).grid(
            row=0, column=1, padx=(8, 0)
        )

        self.status = tk.Label(
            frame, text="Arrêté", fg="red", font=("TkDefaultFont", 12, "bold")
        )
        self.status.grid(row=1, column=0, columnspan=2, pady=(12, 8))

        self.button = tk.Button(frame, text="Démarrer (F8)", command=self.toggle)
        self.button.grid(row=2, column=0, columnspan=2, sticky="ew")

        tk.Label(
            frame,
            text="F8 démarre / arrête la boucle",
            fg="gray",
            font=("TkDefaultFont", 8),
        ).grid(row=3, column=0, columnspan=2, pady=(8, 0))

    # ----- Logique -----------------------------------------------------
    def _read_delay(self):
        try:
            value = int(self.delay_var.get())
            return max(1, value)  # au moins 1 ms pour ne pas saturer le CPU
        except ValueError:
            return self.delay_ms

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
        if key == TOGGLE_KEY:
            # On revient sur le thread tkinter pour manipuler l'UI sans risque.
            self.root.after(0, self.toggle)

    def _update_ui(self):
        if self.running:
            self.status.config(text="En cours", fg="green")
            self.button.config(text="Arrêter (F8)")
        else:
            self.status.config(text="Arrêté", fg="red")
            self.button.config(text="Démarrer (F8)")

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
