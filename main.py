# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 18:54:51 2025

@author: lukas
"""

import tkinter as tk
from tkinter import ttk
import time
import pygame
import winsound
from bestiary_data import bestiary_dict, bosstiary_dict


def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Homework")
        self.root.geometry("500x650")

        # --- SEKCJA GÓRNA ---
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side="top", fill="x", padx=10, pady=5)

        self.is_on_top = False

        self.btn_on_top = tk.Button(self.top_frame,
                                    text="📌 Pin",
                                    command=self.toggle_always_on_top,
                                    relief="raised",
                                    bg="#f0f0f0")
        self.btn_on_top.pack(side="right")


        # --- ZAKŁADKI ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)
        self.tab5 = ttk.Frame(self.notebook)
        self.tab6 = ttk.Frame(self.notebook)
        self.tab7 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text="Fishes Timer")
        self.notebook.add(self.tab2, text="Boss timer")
        self.notebook.add(self.tab3, text="Putrefactory Totem")
        self.notebook.add(self.tab4, text="Imbues")
        self.notebook.add(self.tab5, text="Wpn Exp")
        self.notebook.add(self.tab6, text="Flask")
        self.notebook.add(self.tab7, text="T")

        # --- USTAWIENIA DRAG & DROP (PRZESUWANIE OKNA) ---
        # Podpinamy funkcje przesuwania pod tło karty tab6
        self.tab6.bind("<Button-1>", self.start_move)
        self.tab6.bind("<B1-Motion>", self.do_move)

        # Opcjonalnie: podpinamy pod górny pasek (tam gdzie przycisk PIN)
        self.top_frame.bind("<Button-1>", self.start_move)
        self.top_frame.bind("<B1-Motion>", self.do_move)

        # Opcjonalnie: podpinamy pod wszystkie inne karty
        for t in [self.tab1, self.tab2, self.tab3, self.tab4, self.tab5, self.tab6, self.tab7]:
            t.bind("<Button-1>", self.start_move)
            t.bind("<B1-Motion>", self.do_move)

        # --- TREŚĆ ZAKŁADEK (SKRÓCONA DLA CZYTELNOŚCI - BEZ ZMIAN) ---

        # Zakładka 1: Fishes
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

        # Zakładka 2: Boss
        self.default_time_boss = 90
        self.boss_running = False
        self.boss_start_time = None
        ttk.Label(self.tab2, text="Boss Timer", font=("Arial", 14)).pack(pady=5)
        self.boss_timer_display = ttk.Label(self.tab2, text=format_time(self.default_time_boss), font=("Arial", 24))
        self.boss_timer_display.pack(pady=5)
        ttk.Button(self.tab2, text="Start", command=self.start_boss_timer).pack(pady=5)
        ttk.Button(self.tab2, text="Stop", command=self.stop_boss_timer).pack(pady=5)
        ttk.Button(self.tab2, text="Restart", command=self.reset_boss_timer).pack(pady=5)

        # Zakładka 3: Totem
        self.wave_directions = ["North", "East", "South", "West"]
        self.current_wave_index = 0
        self.totem_running = False
        ttk.Label(self.tab3, text="Putrefactory Totem Timer", font=("Arial", 14)).pack(pady=5)
        self.totem_display = ttk.Label(self.tab3, text=f"Next wave: {self.wave_directions[self.current_wave_index]}",
                                       font=("Arial", 18))
        self.totem_display.pack(pady=5)
        ttk.Button(self.tab3, text="Start", command=self.start_totem_timer).pack(pady=5)
        ttk.Button(self.tab3, text="Stop", command=self.stop_totem_timer).pack(pady=5)

        # Zakładka 4: Imbues
        self.imbue_output = tk.Text(self.tab4, height=5, width=30, state=tk.DISABLED)
        self.imbue_output.pack(pady=5)
        imbues = ["Life leech", "Mana leech", "Critical hit", "Death protection", "Holy protection", "Earth protection",
                  "Ice protection", "Energy protection", "Fire protection", 'Speed', 'Paralysis', 'Capacity',
                  'Fist fighting', 'Magic level']
        imbue_frame = ttk.Frame(self.tab4)
        imbue_frame.pack()
        for index, imbue in enumerate(imbues):
            row, col = divmod(index, 2)
            ttk.Button(imbue_frame, text=imbue, command=lambda n=imbue: self.show_imbue(n)).grid(row=row, column=col,
                                                                                                 padx=5, pady=2,
                                                                                                 sticky="ew")
        imbue_frame.grid_columnconfigure(0, weight=1)
        imbue_frame.grid_columnconfigure(1, weight=1)

        # Zakładka 5: Wpn Exp
        self.log_input = tk.Text(self.tab5, height=15, width=45)
        self.log_input.pack(pady=5)
        ttk.Button(self.tab5, text="Analizuj", command=self.analyze_log).pack(pady=5)
        self.result_labels = {}
        for cat in ["trivial", "easy", "medium", "hard", "challenging", "bane", "archfoe", "nemesis"]:
            frame = ttk.Frame(self.tab5)
            frame.pack(fill="x", padx=10, pady=2)
            ttk.Label(frame, text=cat.capitalize(), width=12).pack(side="left")
            self.result_labels[cat] = ttk.Label(frame, text="")
            self.result_labels[cat].pack(side="left", padx=130)
        frame = ttk.Frame(self.tab5)
        frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame, text="Total", width=12).pack(side="left")
        self.result_total = ttk.Label(frame, text="")
        self.result_total.pack(side="right", padx=50)
        self.result_creatures_total = ttk.Label(frame, text="")
        self.result_creatures_total.pack(side="right")

        # Zakładka 6: Flask
        self.flask_running = False
        self.flask_end_time = 0
        self.lbl_flask_countdown = ttk.Label(self.tab6, text="Ready", font=("Arial", 22, "bold"), foreground="green")
        self.lbl_flask_countdown.pack(pady=(40, 10))
        self.lbl_flask_usage = ttk.Label(self.tab6, text="Flask used: --:--:--", font=("Arial", 12))
        self.lbl_flask_usage.pack(pady=10)
        self.btn_flask = tk.Button(self.tab6, text="USE FLASK", command=self.use_flask, font=("Arial", 14, "bold"),
                                   bg="#dddddd", activebackground="#cccccc")
        self.btn_flask.pack(pady=30, ipadx=30, ipady=15)

        # Zakładka 7: T

        self.t_running = False
        self.t_start_time = 0
        self.t_duration = 0
        pygame.mixer.init()
        pygame.mixer.music.load("Alarm02.wav")
        pygame.mixer.music.set_volume(0.35)

        top = ttk.Frame(self.tab7)
        top.pack(pady=15)

        ttk.Label(top, text="Sekundy:").pack(side="left", padx=(0, 5))

        self.seconds_var = tk.StringVar(value="60")

        self.seconds_entry = ttk.Entry(
            top,
            textvariable=self.seconds_var,
            width=8,
            justify="center"
        )
        self.seconds_entry.pack(side="left", padx=(0, 10))

        ttk.Button(top, text="Start", command=self.start_t_timer).pack(side="left", padx=5)
        ttk.Button(top, text="Stop", command=self.stop_t_timer).pack(side="left", padx=5)

        self.t_timer_display = ttk.Label(
            self.tab7,
            text="01:00",
            font=("Arial", 24)
        )
        self.t_timer_display.pack(pady=30)

    # ====== METODY PRZESUWANIA (DRAG & DROP) ======
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    # ====== FUNKCJA ALWAYS ON TOP ======
    def toggle_always_on_top(self):
        self.is_on_top = not self.is_on_top
        self.root.attributes("-topmost", self.is_on_top)
        if self.is_on_top:
            self.btn_on_top.config(relief="sunken", bg="#90ee90", text="📌 PINNED")
        else:
            self.btn_on_top.config(relief="raised", bg="#f0f0f0", text="📌 Pin")

    # ... (Reszta metod: analyze_log, show_imbue, timery, use_flask - BEZ ZMIAN) ...
    def analyze_log(self):
        # (Tutaj wklej zawartość poprzedniej funkcji analyze_log, żeby nie dublować kodu w odpowiedzi)
        log_text = self.log_input.get("1.0", tk.END).strip().lower()
        lines = log_text.splitlines()
        try:
            start_index = lines.index("killed monsters:") + 1
        except ValueError:
            print("[DEBUG] Nie znaleziono sekcji 'Killed Monsters:'")
            return
        multipliers = {"trivial": 30, "easy": 70, "medium": 100, "hard": 165, "challenging": 240, "bane": 500,
                       "archfoe": 5000, "nemesis": 15000}
        totals = {cat: 0 for cat in multipliers}
        missing_mobs = []
        creatures_count = {cat: 0 for cat in multipliers}
        total_creatures = 0
        for line in lines[start_index:]:
            line = line.strip()
            if not line or line.startswith("looted items:"): break
            if "x " not in line: continue
            try:
                count_str, name = line.split("x ", 1)
                count = eval(count_str.strip())
                name = name.strip().lower()
            except:
                continue
            category = bestiary_dict.get(name)
            if category and category.lower() in multipliers:
                cat_lower = category.lower()
                totals[cat_lower] += count * multipliers[cat_lower]
                creatures_count[cat_lower] += count
                total_creatures += count
            else:
                missing_mobs.append(name)
        total_exp = sum(totals.values())
        for cat, total in totals.items(): self.result_labels[cat].config(text=f"{total} ({creatures_count[cat]} mobs)")
        self.result_total.config(text=str(total_exp))
        self.result_creatures_total.config(text=str(total_creatures))

    def show_output(self, text):
        self.imbue_output.config(state=tk.NORMAL)
        self.imbue_output.delete("1.0", tk.END)
        self.imbue_output.insert(tk.END, text)
        self.imbue_output.config(state=tk.DISABLED)

    def show_imbue(self, name):
        imbue_dict = {'Life leech': '25 Vampire Teeth\n15 Bloody Pincers\n5 Piece of Dead Brain',
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
                      'Magic level': '25 Elvish Talismans\n15 Broken Shamanic Staffs\n15 Strands of Medusa Hair'}
        self.show_output(imbue_dict.get(name, "Brak danych"))

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

    def use_flask(self):
        now = time.time()
        usage_time_str = time.strftime('%H:%M:%S', time.localtime(now))
        self.lbl_flask_usage.config(text=f"Flask used: {usage_time_str}")
        self.flask_end_time = now + (30 * 60)
        self.flask_running = True
        self.lbl_flask_countdown.config(foreground="black")
        self.update_flask_timer()

    def update_flask_timer(self):
        if not self.flask_running: return
        remaining_seconds = int(self.flask_end_time - time.time())
        if remaining_seconds <= 0:
            self.flask_running = False
            self.lbl_flask_countdown.config(text="EXPIRED!", foreground="red")
            return
        mins = remaining_seconds // 60
        secs = remaining_seconds % 60
        self.lbl_flask_countdown.config(text=f"{mins}m{secs:02}s remaining")
        self.root.after(1000, self.update_flask_timer)

    def start_t_timer(self):
        if self.t_running:
            return

        try:
            self.t_duration = int(self.seconds_var.get())
        except ValueError:
            return

        self.seconds_entry.config(state="disabled")
        self.t_running = True
        self.t_start_time = time.time()
        self.update_t_timer()

    def stop_t_timer(self):
        self.t_running = False
        self.seconds_entry.config(state="normal")

    def update_t_timer(self):
        if not self.t_running:
            return

        elapsed = int(time.time() - self.t_start_time)
        remaining = max(0, self.t_duration - elapsed)

        self.t_timer_display.config(text=format_time(remaining))

        if remaining > 0:
            self.root.after(100, self.update_t_timer)
        else:
            self.t_running = False
            self.seconds_entry.config(state="normal")

            pygame.mixer.music.play()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()