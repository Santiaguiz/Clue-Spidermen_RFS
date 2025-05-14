import tkinter as tk
from tkinter import ttk
import random
from PIL import Image, ImageTk  # Pillow must be installed (pip install pillow)
import os

class StartScreen(tk.Toplevel):
    def __init__(self, master, start_callback, background_image_path=None):
        super().__init__(master)
        self.start_callback = start_callback
        self.title("Inicio - Juego Clue Marvel Edition")
        self.geometry("900x600")
        self.resizable(False, False)

        if background_image_path and os.path.isfile(background_image_path):
            img = Image.open(background_image_path)
            img = img.resize((900, 600), Image.ANTIALIAS)
            self.bg_image = ImageTk.PhotoImage(img)
            self.background_label = tk.Label(self, image=self.bg_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.configure(bg="#1c1c1c")

        overlay = tk.Frame(self, bg="#000000", bd=0, highlightthickness=0)
        overlay.place(relx=0.5, rely=0.5, anchor="center")

        welcome_label = tk.Label(overlay, text="Juego Clue - Adivina al Culpable (Marvel Edition)",
                                 font=("Russo One", 25, "bold"), fg="#f0b429", bg="#000000", justify=tk.CENTER)
        welcome_label.pack(pady=(0, 30))

        start_button = tk.Button(overlay, text="Iniciar Juego", font=("Russo One", 16, "bold"),
                                 bg="#f0b429", fg="#222", padx=20, pady=10, command=self.start_game)
        start_button.pack()

        self.protocol("WM_DELETE_WINDOW", self.master.destroy)

    def start_game(self):
        self.start_callback()
        self.destroy()

class ClueGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Juego Clue - Adivina al Culpable (Marvel Edition)")
        self.geometry("920x750")
        self.configure(bg="#1c1c1c")
        self.resizable(False, False)

        self.withdraw()

        self.characters = [
            "Peter Parker",
            "Miles Morales",
            "Gwen Stacy",
            "Miguel O'Hara",
            "Cindy Moon"
        ]
        self.locations = [
            "Torre Avengers",
            "Sanctum Sanctorum",
            "Wakanda",
            "Asgard",
            "Helicarger"
        ]
        self.weapons = [
            "Telaraña",
            "Guantelete del Infinito",
            "Mjolnir",
            "Escudo del Capitán América",
            "Armadura de Iron Man"
        ]

        self.image_base_path = "images"
        self.char_img_path = os.path.join(self.image_base_path, "characters")
        self.loc_img_path = os.path.join(self.image_base_path, "locations")
        self.weap_img_path = os.path.join(self.image_base_path, "weapons")

        # Narrativas base sin revelar la solución
        self.stories = [
            "Una sombra misteriosa acechaba cerca de un lugar importante el día del incidente.",
            "Los rumores indican que alguien discutió acaloradamente en una locación tranquila justo antes de la tragedia.",
            "Testigos mencionan haber visto un objeto inusual cerca de la escena del crimen.",
            "Un conocido personaje fue visto desaparecido justo antes de que ocurriera el evento fatal.",
            "El ambiente estaba tenso en una locación remota, y un objeto peculiar llamó la atención de varios."
        ]

        # Frases de indicios para la narrativa inicial que sugieren un arma, locacion o personaje no siendo la solución
        self.clue_indications = {
            "characters": [
                "Alguien rumoró que {} estuvo especialmente nervioso ese día.",
                "Se dice que {} tuvo una discusión con una persona cercana antes del incidente.",
                "{} parecía preocupado por algo que ocurrió últimamente."
            ],
            "locations": [
                "Una sombra fue vista rondando alrededor de {} en la noche del incidente.",
                "Se escucharon ruidos extraños provenientes de {} justo antes de que todo pasara.",
                "{} ha sido un lugar de frecuentes conflictos últimamente."
            ],
            "weapons": [
                "Un objeto similar a {} fue encontrado cerca de la escena.",
                "Conteo de {} en la escena sugiere que podría ser un arma importante.",
                "Alguien fue visto manipulando un {} horas antes del suceso."
            ]
        }

        self.max_clues = 5
        self.clues_spent = 0  # pistas + interrogatorios usados
        self.hints_added = set()
        self.solution = {}
        self.coartadas = {}

        self.char_images = {}
        self.loc_images = {}
        self.weap_images = {}

        # Crear notebook de pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear pestañas
        self.tab_story = ttk.Frame(self.notebook)
        self.tab_investigate = ttk.Frame(self.notebook)
        self.tab_guess = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_story, text="Narrativa Inicial")
        self.notebook.add(self.tab_investigate, text="Interrogar & Pistas")
        self.notebook.add(self.tab_guess, text="Hacer Adivinanza")

        # Construir contenido de cada pestaña
        self.create_story_tab()
        self.create_investigate_tab()
        self.create_guess_tab()

        # Inicio oculto hasta que termine start screen
        self.withdraw()

        start_bg_path = os.path.join("images", "start_background.png")
        self.start_screen = StartScreen(self, self.start_after_screen, background_image_path=start_bg_path)
        self.start_screen.grab_set()

    def start_after_screen(self):
        self.deiconify()
        self.new_game()
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.notebook.select(self.tab_story)

    # ----- Pestaña Narrativa -----
    def create_story_tab(self):
        lbl_title = tk.Label(self.tab_story, text="Narrativa Inicial",
                             font=("Russo One", 22, "bold"), fg="#f0b429", bg="#1c1c1c")
        lbl_title.pack(pady=10)

        self.story_text = tk.Text(self.tab_story, width=105, height=10, wrap="word",
                                 font=("Helvetica", 13), bg="#282828", fg="#f0f0f0", bd=0, relief=tk.FLAT)
        self.story_text.pack(padx=20, pady=10)
        self.story_text.configure(state="disabled")

        self.btn_next_from_story = tk.Button(self.tab_story, text="Siguiente", font=("Russo One", 16, "bold"),
                                             bg="#f0b429", fg="#222", padx=25, pady=10, command=self.goto_investigate_tab)
        self.btn_next_from_story.pack(pady=10)

    def goto_investigate_tab(self):
        self.notebook.tab(1, state="normal")
        self.notebook.select(self.tab_investigate)

    # ----- Pestaña Interrogatorios y Pistas -----
    def create_investigate_tab(self):
        lbl_title = tk.Label(self.tab_investigate, text="Interrogar Personajes, Armas o Locaciones",
                             font=("Russo One", 20, "bold"), fg="#f0b429", bg="#1c1c1c")
        lbl_title.pack(pady=8)

        frame_mode = tk.Frame(self.tab_investigate, bg="#1c1c1c")
        frame_mode.pack(pady=8)
        self.mode_var = tk.StringVar(value="Personajes")

        modes = ["Personajes", "Locaciones", "Armas"]
        for i, m in enumerate(modes):
            rb = tk.Radiobutton(frame_mode, text=m, variable=self.mode_var, value=m, font=("Helvetica", 13, "bold"),
                                bg="#1c1c1c", fg="#f0b429", activebackground="#1c1c1c", activeforeground="#f0b429",
                                selectcolor="#1c1c1c", command=self.update_combo_values)
            rb.grid(row=0, column=i, padx=20, sticky="w")

        frame_select = tk.Frame(self.tab_investigate, bg="#1c1c1c")
        frame_select.pack(pady=5, fill="x", padx=10)
        frame_select.columnconfigure(0, weight=1)

        self.select_label = tk.Label(frame_select, text="Seleccionar Personaje:", font=("Helvetica", 13, "bold"), fg="#f0b429", bg="#1c1c1c")
        self.select_label.grid(row=0, column=0, padx=10, sticky="w")

        self.select_choice = ttk.Combobox(frame_select, state="readonly", font=("Helvetica", 12))
        self.select_choice.grid(row=1, column=0, padx=10, sticky="ew")
        self.select_choice.set('')  # No preseleccionado
        self.select_choice.bind("<<ComboboxSelected>>", lambda e: self.on_select_choice())

        # Imagen y texto info
        self.select_image_label = tk.Label(self.tab_investigate, bg="#1c1c1c")
        self.select_image_label.pack(pady=8)

        self.info_text = tk.Text(self.tab_investigate, width=105, height=12, wrap="word", font=("Helvetica", 11),
                                 bg="#333", fg="#eee", bd=0, relief=tk.FLAT)
        self.info_text.pack(padx=10, pady=(0, 12))
        self.info_text.configure(state="disabled")

        # Botones: Pedir pista y Siguiente
        frame_buttons = tk.Frame(self.tab_investigate, bg="#1c1c1c")
        frame_buttons.pack(pady=10)

        self.clue_button = tk.Button(frame_buttons, text="Pedir Pista", font=("Russo One", 14, "bold"),
                                     bg="#444", fg="#f0b429", padx=18, pady=8, command=self.provide_clue)
        self.clue_button.grid(row=0, column=0, padx=12)

        self.btn_next_from_investigate = tk.Button(frame_buttons, text="Siguiente", font=("Russo One", 14, "bold"),
                                                   bg="#f0b429", fg="#222", padx=18, pady=8, command=self.goto_guess_tab)
        self.btn_next_from_investigate.grid(row=0, column=1, padx=12)

        self.clues_label = tk.Label(self.tab_investigate, text="", font=("Helvetica", 13, "italic"),
                                    fg="#f0b429", bg="#1c1c1c")
        self.clues_label.pack(pady=5)

        self.clues_text = tk.Text(self.tab_investigate, width=105, height=5, wrap="word", font=("Helvetica", 11),
                                  bg="#333", fg="#eee", bd=0, relief=tk.FLAT)
        self.clues_text.pack(padx=10, pady=(0,20))
        self.clues_text.configure(state="disabled")

        self.update_combo_values()

    def on_select_choice(self):
        selection = self.select_choice.get()
        if not selection:
            return
        if self.clues_spent >= self.max_clues:
            self.info_insert("\n\nYa no quedan pistas disponibles para interrogar.")
            self.clue_button.config(state="disabled")
            return
        self.provide_interrogation_info()

    def goto_guess_tab(self):
        self.notebook.tab(2, state="normal")
        self.notebook.select(self.tab_guess)

    # ----- Pestaña Adivinanza -----
    def create_guess_tab(self):
        lbl_title = tk.Label(self.tab_guess, text="Adivinanza Final",
                             font=("Russo One", 22, "bold"), fg="#f0b429", bg="#1c1c1c")
        lbl_title.pack(pady=10)

        frame_select = tk.Frame(self.tab_guess, bg="#1c1c1c")
        frame_select.pack(pady=5, fill="x", padx=10)
        frame_select.columnconfigure([0,1,2], weight=1)

        self.guess_char_choice = ttk.Combobox(frame_select, values=self.characters, state="readonly", font=("Helvetica", 13))
        self.guess_char_choice.grid(row=0, column=0, padx=10, pady=8)
        self.guess_char_choice.set('')

        self.guess_loc_choice = ttk.Combobox(frame_select, values=self.locations, state="readonly", font=("Helvetica", 13))
        self.guess_loc_choice.grid(row=0, column=1, padx=10, pady=8)
        self.guess_loc_choice.set('')

        self.guess_weap_choice = ttk.Combobox(frame_select, values=self.weapons, state="readonly", font=("Helvetica", 13))
        self.guess_weap_choice.grid(row=0, column=2, padx=10, pady=8)
        self.guess_weap_choice.set('')

        self.guess_button = tk.Button(self.tab_guess, text="Hacer Adivinanza", font=("Russo One", 16, "bold"),
                                      bg="#f0b429", fg="#222", padx=30, pady=10, command=self.make_guess)
        self.guess_button.pack(pady=15)

        self.guess_result_text = tk.Text(self.tab_guess, width=105, height=15, wrap="word",
                                         font=("Helvetica", 12), bg="#282828", fg="#f0f0f0", bd=0, relief=tk.FLAT)
        self.guess_result_text.pack(padx=10, pady=10)
        self.guess_result_text.configure(state="disabled")

        self.btn_reset = tk.Button(self.tab_guess, text="Juego Nuevo", font=("Russo One", 14, "bold"),
                                   bg="#222", fg="#f0b429", padx=25, pady=8, command=self.reset_to_story_tab)
        self.btn_reset.pack(pady=10)

    def reset_to_story_tab(self):
        self.clues_spent = 0
        self.hints_added.clear()
        self.guess_result_text.configure(state="normal")
        self.guess_result_text.delete("1.0", tk.END)
        self.guess_result_text.configure(state="disabled")
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.configure(state="disabled")
        self.clues_text.configure(state="normal")
        self.clues_text.delete("1.0", tk.END)
        self.clues_text.configure(state="disabled")
        self.clues_label.config(text=f"Pistas disponibles: {self.max_clues}")
        self.new_game()
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.notebook.select(self.tab_story)
        self.clue_button.config(state="normal")
        self.guess_button.config(state="normal")

    def load_image(self, folder, item_name):
        filename = item_name + ".png"
        filepath = os.path.join(folder, filename)
        if not os.path.isfile(filepath):
            return None
        img = Image.open(filepath)
        img = img.resize((100, 100), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)

    def update_combo_values(self):
        mode = self.mode_var.get()
        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.configure(state="disabled")
        self.select_image_label.config(image="", text="")

        if mode == "Personajes":
            values = self.characters
            self.select_label.config(text="Seleccionar Personaje:")
        elif mode == "Locaciones":
            values = self.locations
            self.select_label.config(text="Seleccionar Locación:")
        else:
            values = self.weapons
            self.select_label.config(text="Seleccionar Arma:")

        self.select_choice['values'] = values
        self.select_choice.set('')  # No preseleccionado al cambiar de modo

    def provide_interrogation_info(self):
        if self.clues_spent >= self.max_clues:
            self.info_insert("\n\nYa no quedan pistas disponibles para interrogar.")
            self.clue_button.config(state="disabled")
            return
        selection = self.select_choice.get()
        if not selection:
            return
        mode = self.mode_var.get()
        text, image = "", None

        if mode == "Personajes":
            coartada = self.coartadas.get(selection)
            if coartada:
                text = f"Interrogando a {selection}:\n\n"
                text += f"Coartada: {coartada['alibi']}\n"
                text += "Lugares donde fue visto: " + ", ".join(coartada["places"]) + "\n"
                text += "Armas asociadas o encontradas: " + ", ".join(coartada["weapons"]) + "\n"
            image = self.load_image(self.char_img_path, selection)
        elif mode == "Locaciones":
            text = f"Información sobre la locación: {selection}\n\nPersonajes vistos aquí:\n"
            chars_here = [c for c, data in self.coartadas.items() if selection in data['places']]
            if chars_here:
                text += ", ".join(chars_here)
            else:
                text += "Ninguno"
            text += "\n\nArmas encontradas o asociadas aquí:\n"
            weapons_here = set()
            for c, data in self.coartadas.items():
                if selection in data['places']:
                    weapons_here.update(data['weapons'])
            if weapons_here:
                text += ", ".join(weapons_here)
            else:
                text += "Ninguna"
            image = self.load_image(self.loc_img_path, selection)
        else:
            text = f"Información sobre el arma: {selection}\n\nPersonajes asociados con esta arma:\n"
            holders = [c for c, data in self.coartadas.items() if selection in data['weapons']]
            if holders:
                text += ", ".join(holders)
            else:
                text += "Ninguno"
            image = self.load_image(self.weap_img_path, selection)

        self.info_text.configure(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.configure(state="disabled")

        if image:
            self.select_image_label.config(image=image)
            self.select_image_label.image = image
        else:
            self.select_image_label.config(image="", text="No Img")

        self.use_clue_on_interrogation()

    def info_insert(self, text):
        self.info_text.configure(state="normal")
        self.info_text.insert(tk.END, text)
        self.info_text.see(tk.END)
        self.info_text.configure(state="disabled")

    def use_clue_on_interrogation(self):
        if self.clues_spent >= self.max_clues:
            self.clue_button.config(state="disabled")
            return
        self.clues_spent += 1
        self.clues_label.config(text=f"Pistas disponibles: {self.max_clues - self.clues_spent}")
        if self.clues_spent >= self.max_clues:
            self.clue_button.config(state="disabled")

    def insert_investigate_clue(self, text):
        self.clues_text.configure(state="normal")
        self.clues_text.insert(tk.END, text)
        self.clues_text.see(tk.END)
        self.clues_text.configure(state="disabled")

    def provide_clue(self):
        if self.clues_spent >= self.max_clues:
            self.clues_label.config(text=f"Pistas disponibles: 0")
            self.insert_investigate_clue("\n\nYa no quedan pistas disponibles.")
            self.clue_button.config(state="disabled")
            return

        possible_clues = []

        for c in self.characters:
            if c != self.solution['character'] and ("character:" + c) not in self.hints_added:
                possible_clues.append(("personaje", c))

        for l in self.locations:
            if l != self.solution['location'] and ("location:" + l) not in self.hints_added:
                possible_clues.append(("locacion", l))

        for w in self.weapons:
            if w != self.solution['weapon'] and ("weapon:" + w) not in self.hints_added:
                possible_clues.append(("arma", w))

        if not possible_clues:
            self.clue_button.config(state="disabled")
            self.insert_investigate_clue("\n\nYa no quedan pistas disponibles.")
            return

        clue_type, clue_value = random.choice(possible_clues)

        if clue_type == "personaje":
            clue_text = f"La persona culpable no es {clue_value}."
            self.hints_added.add("character:" + clue_value)
        elif clue_type == "locacion":
            clue_text = f"No ocurrió en el lugar llamado {clue_value}."
            self.hints_added.add("location:" + clue_value)
        else:
            clue_text = f"No se usó el arma {clue_value}."
            self.hints_added.add("weapon:" + clue_value)

        self.clues_spent += 1
        self.clues_label.config(text=f"Pistas disponibles: {self.max_clues - self.clues_spent}")

        self.insert_investigate_clue("\n\n" + clue_text)

        if self.clues_spent >= self.max_clues:
            self.clue_button.config(state="disabled")
            self.insert_investigate_clue("\n\nHas agotado todas las pistas.\nSigue intentando hacer tu adivinanza.")

    def make_guess(self):
        guess_char = self.guess_char_choice.get()
        guess_loc = self.guess_loc_choice.get()
        guess_weap = self.guess_weap_choice.get()

        if not guess_char or not guess_loc or not guess_weap:
            self.guess_result_text.configure(state="normal")
            self.guess_result_text.delete("1.0", tk.END)
            self.guess_result_text.insert(tk.END, "Por favor, selecciona un Personaje, una Locación y un Arma para hacer la adivinanza.")
            self.guess_result_text.configure(state="disabled")
            return

        correct = (guess_char == self.solution['character'] and
                   guess_loc == self.solution['location'] and
                   guess_weap == self.solution['weapon'])

        self.guess_result_text.configure(state="normal")
        self.guess_result_text.delete("1.0", tk.END)
        if correct:
            narrative = (
                f"¡Felicidades! Has adivinado correctamente:\n\n"
                f"🔸 Culpable: {self.solution['character']}\n"
                f"🔸 Locación: {self.solution['location']}\n"
                f"🔸 Arma: {self.solution['weapon']}\n\n"
                "¡La verdad ha sido revelada! 🎉"
            )
            self.guess_result_text.insert(tk.END, narrative)
            self.guess_button.config(state="disabled")
            self.clue_button.config(state="disabled")
        else:
            narrative = (
                f"Respuesta incorrecta.\n\n"
                f"La verdad era:\n"
                f"🔸 Culpable: {self.solution['character']}\n"
                f"🔸 Locación: {self.solution['location']}\n"
                f"🔸 Arma: {self.solution['weapon']}\n\n"
                "Sigue investigando y no te rindas!"
            )
            self.guess_result_text.insert(tk.END, narrative)
            self.guess_button.config(state="disabled")
            self.clue_button.config(state="disabled")
        self.guess_result_text.configure(state="disabled")

    def new_game(self):
        self.clues_spent = 0
        self.hints_added.clear()

        idx_character = random.randint(0, len(self.characters) - 1)
        idx_location = random.randint(0, len(self.locations) - 1)
        idx_weapon = random.randint(0, len(self.weapons) - 1)

        self.solution['character'] = self.characters[idx_character]
        self.solution['location'] = self.locations[idx_location]
        self.solution['weapon'] = self.weapons[idx_weapon]

        # Elegir víctima al azar distinta al culpable para la narrativa
        victim = random.choice([c for c in self.characters if c != self.solution['character']])

        # Elegir indicio para narrativa inicial sin revelar solución
        # Puede ser personaje, locacion o arma que NO sea parte de la solución
        clue_type = random.choice(["characters", "locations", "weapons"])
        if clue_type == "characters":
            clue_options = [c for c in self.characters if c != self.solution['character']]
            clue_entity = random.choice(clue_options)
        elif clue_type == "locations":
            clue_options = [l for l in self.locations if l != self.solution['location']]
            clue_entity = random.choice(clue_options)
        else:
            clue_options = [w for w in self.weapons if w != self.solution['weapon']]
            clue_entity = random.choice(clue_options)

        base_story = random.choice(self.stories)
        indication_phrase = random.choice(self.clue_indications[clue_type]).format(clue_entity)

        narrative = (
            f"Una tragedia ha ocurrido: {victim} ha sido encontrado muerto.\n\n"
            f"{base_story}\n{indication_phrase}\n\n"
            "La investigación comienza y debes descubrir la verdad."
        )

        self.story_text.configure(state="normal")
        self.story_text.delete("1.0", tk.END)
        self.story_text.insert(tk.END, narrative)
        self.story_text.configure(state="disabled")

        self.mode_var.set("Personajes")
        self.update_combo_values()

        self.guess_char_choice.set('')
        self.guess_loc_choice.set('')
        self.guess_weap_choice.set('')

        self.coartadas.clear()
        for character in self.characters:
            if character == self.solution['character']:
                alibi = (f"Se sabe que {character} estuvo visto cerca de {self.solution['location']}, "
                         f"aunque no hay pruebas claras de lo que hizo con {self.solution['weapon']}.")
                places = [self.solution['location']]
                weapons = [self.solution['weapon']]
            else:
                fake_loc = random.choice([l for l in self.locations if l != self.solution['location']])
                fake_weap = random.choice([w for w in self.weapons if w != self.solution['weapon']])
                alibi = f"Afirmó haber estado en {fake_loc} durante el incidente, y no portar ningún arma peculiar."
                places = [fake_loc]
                weapons = [fake_weap]

            self.coartadas[character] = {
                "alibi": alibi,
                "places": places,
                "weapons": weapons
            }

        self.clues_label.config(text=f"Pistas disponibles: {self.max_clues - self.clues_spent}")
        self.clues_text.configure(state="normal")
        self.clues_text.delete("1.0", tk.END)
        self.clues_text.configure(state="disabled")

        self.guess_result_text.configure(state="normal")
        self.guess_result_text.delete("1.0", tk.END)
        self.guess_result_text.configure(state="disabled")

        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.clue_button.config(state="normal")
        self.guess_button.config(state="normal")

if __name__ == "__main__":
    app = ClueGame()
    app.mainloop()

