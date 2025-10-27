# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 18:54:51 2025

@author: lukas
"""

import tkinter as tk
from tkinter import ttk
import time
from bestiary_data import bestiary_dict, bosstiary_dict  # słownik mobów

def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Homework")
        self.root.geometry("500x600")

        # Tworzymy notebook (zakładki)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # Zakładki
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)
        self.tab5 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="Fishes Timer")
        self.notebook.add(self.tab2, text="Boss timer")
        self.notebook.add(self.tab3, text="Putrefactory Totem")
        self.notebook.add(self.tab4, text="Imbues")
        self.notebook.add(self.tab5, text="Wpn Exp")

        # --- Zakładka 1: Fishes Timer ---
        self.default_time_fishes = 120
        self.fishes_start_time = None
        self.time_left_fishes = self.default_time_fishes
        self.fishes_running = False

        ttk.Label(self.tab1, text="Fishes Timer", font=("Arial", 14)).pack(pady=5)
        self.fishes_timer_display = ttk.Label(self.tab1, text=format_time(self.time_left_fishes), font=("Arial", 24))
        self.fishes_timer_display.pack(pady=5)

        ttk.Button(self.tab1, text="Start", command=self.start_fishes_timer).pack(pady=5)
        ttk.Button(self.tab1, text="Stop", command=self.stop_fishes_timer).pack(pady=5)
        ttk.Button(self.tab1, text="Restart", command=self.reset_fishes_timer).pack(pady=5)

        # --- Zakładka 2: Boss Timer ---
        self.default_time_boss = 90
        self.boss_running = False
        self.boss_start_time = None

        ttk.Label(self.tab2, text="Boss Timer", font=("Arial", 14)).pack(pady=5)
        self.boss_timer_display = ttk.Label(self.tab2, text=format_time(self.default_time_boss), font=("Arial", 24))
        self.boss_timer_display.pack(pady=5)

        ttk.Button(self.tab2, text="Start", command=self.start_boss_timer).pack(pady=5)
        ttk.Button(self.tab2, text="Stop", command=self.stop_boss_timer).pack(pady=5)
        ttk.Button(self.tab2, text="Restart", command=self.reset_boss_timer).pack(pady=5)

        # --- Zakładka 3: Putrefactory Totem ---
        self.wave_directions = ["North", "East", "South", "West"]
        self.current_wave_index = 0
        self.totem_running = False

        ttk.Label(self.tab3, text="Putrefactory Totem Timer", font=("Arial", 14)).pack(pady=5)
        self.totem_display = ttk.Label(self.tab3, text=f"Next wave: {self.wave_directions[self.current_wave_index]}", font=("Arial", 18))
        self.totem_display.pack(pady=5)
        ttk.Button(self.tab3, text="Start", command=self.start_totem_timer).pack(pady=5)
        ttk.Button(self.tab3, text="Stop", command=self.stop_totem_timer).pack(pady=5)

        # --- Zakładka 4: Imbues ---
        self.imbue_output = tk.Text(self.tab4, height=5, width=30, state=tk.DISABLED)
        self.imbue_output.pack(pady=5)

        imbues = ["Life leech", "Mana leech", "Critical hit", "Death protection",
                  "Holy protection", "Earth protection", "Ice protection",
                  "Energy protection", "Fire protection", 'Speed', 'Paralysis', 'Capacity', 'Fist fighting', 'Magic level']

        imbue_frame = ttk.Frame(self.tab4)
        imbue_frame.pack()
        for index, imbue in enumerate(imbues):
            row, col = divmod(index, 2)
            ttk.Button(imbue_frame, text=imbue, command=lambda n=imbue: self.show_imbue(n)).grid(row=row, column=col, padx=5, pady=2, sticky="ew")

        imbue_frame.grid_columnconfigure(0, weight=1)
        imbue_frame.grid_columnconfigure(1, weight=1)

        # --- Zakładka 5: Wpn Exp ---
        self.log_input = tk.Text(self.tab5, height=15, width=45)
        self.log_input.pack(pady=5)
        ttk.Button(self.tab5, text="Analizuj", command=self.analyze_log).pack(pady=5)

        self.result_labels = {}
        for cat in ["trivial", "easy", "medium", "hard", "challenging"]:
            frame = ttk.Frame(self.tab5)
            frame.pack(fill="x", padx=10, pady=2)
            ttk.Label(frame, text=cat.capitalize(), width=12).pack(side="left")
            self.result_labels[cat] = ttk.Label(frame, text="0")
            self.result_labels[cat].pack(side="right")

        frame = ttk.Frame(self.tab5)
        frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame, text="Total Exp", width=12).pack(side="left")
        self.result_total = ttk.Label(frame, text="0")
        self.result_total.pack(side="right")

    # ====== LOG ANALYZER ======
    def analyze_log(self):
        log_text = self.log_input.get("1.0", tk.END).strip().lower()
        lines = log_text.splitlines()

        try:
            start_index = lines.index("killed monsters:") + 1
        except ValueError:
            print("[DEBUG] Nie znaleziono sekcji 'Killed Monsters:'")
            return

        multipliers = {
            "trivial": 30,
            "easy": 70,
            "medium": 100,
            "hard": 165,
            "challenging": 240,
            "bane": 500,
            "archfoe": 5000,
            "nemesis": 15000
        }

        totals = {cat: 0 for cat in multipliers}
        missing_mobs = []

        for line in lines[start_index:]:
            line = line.strip()
            if not line or line.startswith("looted items:"):
                break
            if "x " not in line:
                continue

            try:
                count_str, name = line.split("x ", 1)
                count = eval(count_str.strip())  # obsługa np. 150+50
                name = name.strip().capitalize()
            except Exception as e:
                print(f"[DEBUG] Błąd parsowania '{line}': {e}")
                continue

            category = bestiary_dict.get(name)
            if category:
                category = category.lower()
                if category in multipliers:
                    totals[category] += count * multipliers[category]
            else:
                missing_mobs.append(name)

        total_exp = sum(totals.values())
        for cat, total in totals.items():
            self.result_labels[cat].config(text=str(total))
        self.result_total.config(text=str(total_exp))

        if missing_mobs:
            print("[DEBUG] Brakujące moby:")
            for mob in missing_mobs:
                print(" -", mob)

    # ====== IMBUES ======
    def show_output(self, text):
        self.imbue_output.config(state=tk.NORMAL)
        self.imbue_output.delete("1.0", tk.END)
        self.imbue_output.insert(tk.END, text)
        self.imbue_output.config(state=tk.DISABLED)

    def show_imbue(self, name):
        imbue_dict = {
            'Life leech': '25 Vampire Teeth\n15 Bloody Pincers\n5 Piece of Dead Brain',
            'Mana leech': '25 Rope Belts\n25 Silencer Claws\n5 Some Grimeleech Wings',
            'Critical hit': '20 Protective Charms\n25 Sabreteeth\n5 Vexclaw Talons',
            'Death protection': '25 Flasks of Embalming Fluid\n20 Gloom Wolf Furs\n5 Mystical Hourglasses',
            'Earth protection': '25 Pieces of Swampling Wood\n20 Snake Skins\n10 Brimstone Fangs',
            'Fire protection': '20 Green Dragon Leathers\n10 Blazing Bones\n5 Draken Sulphur',
            'Ice protection': '25 Winter Wolf Furs\n15 Thick Furs\n10 Deepling Warts',
            'Energy protection': '20 Wyvern Talismans\n15 Crawler Head Platings\n10 Wyrm Scales',
            'Holy protection': '25 Cultish Robes\n25 Cultish Masks\n20 Hellspawn Tails',
            'Speed': '15 Damselfly Wings\n25 Compasses\n20 Waspoid Wings',
            'Paralysis': '20 Wereboar Hooves\n15 Crystalized Anger\n5 Quills',
            'Capacity': '20 Fairy Wings\n10 Little Bowls of Myrrh\n5 Goosebump Leather',
            'Fist fighting': '20 Tarantula Egg\n25 Mantassin Tails\n10 Gold-Brocaded Cloth',
            'Magic level': '25 Elvish Talismans\n15 Broken Shamanic Staffs\n15 Strands of Medusa Hair'
        }
        self.show_output(imbue_dict.get(name, "Brak danych"))

    # ====== TIMERY ======
    def update_fishes_timer(self):
        if self.fishes_running:
            elapsed = int(time.time() - self.fishes_start_time)
            remaining = max(0, self.default_time_fishes - elapsed)
            self.fishes_timer_display.config(text=format_time(remaining))
            if remaining > 0:
                self.root.after(100, self.update_fishes_timer)
            else:
                self.fishes_start_time = time.time()
                self.update_fishes_timer()

    def start_fishes_timer(self):
        if not self.fishes_running:
            self.fishes_running = True
            self.fishes_start_time = time.time()
            self.update_fishes_timer()

    def stop_fishes_timer(self):
        self.fishes_running = False

    def reset_fishes_timer(self):
        self.fishes_running = False
        self.time_left_fishes = self.default_time_fishes
        self.fishes_timer_display.config(text=format_time(self.time_left_fishes))

    def update_boss_timer(self):
        if self.boss_running:
            elapsed = int(time.time() - self.boss_start_time)
            remaining = max(0, self.default_time_boss - elapsed)
            self.boss_timer_display.config(text=format_time(remaining))
            if remaining > 0:
                self.root.after(100, self.update_boss_timer)
            else:
                self.boss_start_time = time.time()
                self.update_boss_timer()

    def start_boss_timer(self):
        if not self.boss_running:
            self.boss_running = True
            self.boss_start_time = time.time()
            self.update_boss_timer()

    def stop_boss_timer(self):
        self.boss_running = False

    def reset_boss_timer(self):
        self.boss_running = False
        self.boss_timer_display.config(text=format_time(self.default_time_boss))

    def update_totem_timer(self):
        if self.totem_running:
            self.current_wave_index = (self.current_wave_index + 1) % len(self.wave_directions)
            self.totem_display.config(text=f"Next wave: {self.wave_directions[self.current_wave_index]}")
            self.root.after(6000, self.update_totem_timer)

    def start_totem_timer(self):
        if not self.totem_running:
            self.totem_running = True
            self.update_totem_timer()

    def stop_totem_timer(self):
        self.totem_running = False


if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()
