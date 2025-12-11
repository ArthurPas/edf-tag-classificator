import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image, ImageOps
import os
import re

# --- CONFIGURATION DES CHEMINS ---

ORIGINALS_DIR = "data/end_to_end"
CROPS_DIR = "cropped_output"
TAGS_FILE = "found_tags.txt"

class ImageBrowserApp:
    def __init__(self, master, originals_path, crops_path, tags_path):
        self.master = master
        self.master.title("Visualiseur Côte à Côte (Split View)")
        self.master.geometry("1600x900") # Fenêtre large pour le mode côte à côte
        
        self.originals_path = originals_path
        self.crops_path = crops_path
        self.tags_path = tags_path
        
        self.tags_dict = self.load_tags()
        self.image_groups = self.scan_folders_robust()
        self.group_keys = sorted(list(self.image_groups.keys()))
        self.index = 0

        # --- 1. Zone de Navigation (Tout en haut) ---
        control_frame = ttk.Frame(master)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.prev_btn = ttk.Button(control_frame, text="<< Précédent", command=self.prev_image)
        self.prev_btn.pack(side=tk.LEFT)

        self.lbl_info = ttk.Label(control_frame, text="...", font=("Arial", 11, "bold"))
        self.lbl_info.pack(side=tk.LEFT, expand=True)

        self.next_btn = ttk.Button(control_frame, text="Suivant >>", command=self.next_image)
        self.next_btn.pack(side=tk.RIGHT)

        # --- 2. Conteneur Principal (PanedWindow) ---
        # Permet de séparer l'écran en gauche/droite avec une barre mobile
        self.paned_window = tk.PanedWindow(master, orient=tk.HORIZONTAL, sashwidth=5, bg="#d9d9d9")
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Partie GAUCHE : Originale ---
        self.orig_frame = ttk.LabelFrame(self.paned_window, text="Image Source")
        # On l'ajoute au volet gauche
        self.paned_window.add(self.orig_frame, width=900) # Largeur initiale 900px
        
        self.lbl_orig_img = ttk.Label(self.orig_frame)
        self.lbl_orig_img.pack(expand=True, fill=tk.BOTH)

        # --- Partie DROITE : Crops ---
        self.crops_frame_container = ttk.LabelFrame(self.paned_window, text="Extractions & Tags")
        # On l'ajoute au volet droit
        self.paned_window.add(self.crops_frame_container)

        # Configuration du scroll pour la partie droite
        self.canvas = tk.Canvas(self.crops_frame_container)
        self.scrollbar = ttk.Scrollbar(self.crops_frame_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Ajustement automatique de la largeur du contenu scrollable
        def configure_canvas(event):
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        self.canvas.bind("<Configure>", configure_canvas)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        self.tk_images_refs = []

        if self.group_keys:
            self.show_current_group()
        else:
            self.lbl_info.config(text="Aucune image trouvée.")

    def _on_mousewheel(self, event):
        if self.canvas.bbox("all")[3] > self.canvas.winfo_height():
            if event.num == 5 or event.delta < 0: self.canvas.yview_scroll(1, "units")
            elif event.num == 4 or event.delta > 0: self.canvas.yview_scroll(-1, "units")

    def load_tags(self):
        tags = {}
        if not os.path.exists(self.tags_path): return {}
        try:
            with open(self.tags_path, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line:
                        filename, tag = line.strip().split(":", 1)
                        tags[filename.strip()] = tag.strip()
        except: pass
        return tags

    def scan_folders_robust(self):
        # (Même logique robuste que précédemment)
        groups = {}
        if not os.path.exists(self.originals_path) or not os.path.exists(self.crops_path): return {}

        orig_files = sorted([f for f in os.listdir(self.originals_path) if f.lower().endswith(('.jpg','.jpeg','.png','.bmp','.tiff'))])
        crop_files = sorted(os.listdir(self.crops_path))
        index_pattern = re.compile(r"_(\d+)\.")

        for orig in orig_files:
            base_name = os.path.splitext(orig)[0]
            found_crops = []
            for crop in crop_files:
                if crop.lower().startswith(base_name.lower()) or crop.lower().startswith(orig.lower()):
                    if index_pattern.search(crop):
                        found_crops.append(crop)

            def get_index(fname):
                matches = re.findall(r"_(\d+)\.", fname)
                return int(matches[-1]) if matches else 0

            found_crops.sort(key=get_index)
            groups[orig] = found_crops
        return groups

    def show_current_group(self):
        self.tk_images_refs = [] 
        for w in self.scrollable_frame.winfo_children(): w.destroy()

        if not self.group_keys: return

        orig_filename = self.group_keys[self.index]
        crop_files = self.image_groups[orig_filename]
        
        self.lbl_info.config(text=f"{self.index + 1}/{len(self.group_keys)}: {orig_filename} ({len(crop_files)} crops)")

        # --- 1. Affichage Original (Gauche) ---
        try:
            img = Image.open(os.path.join(self.originals_path, orig_filename))
            img = img.rotate(270, expand=True)
            # On adapte la taille max pour qu'elle tienne dans la moitié gauche (ex: 900x900)
            img = ImageOps.contain(img, (900, 900))
            tk_img = ImageTk.PhotoImage(img)
            self.lbl_orig_img.config(image=tk_img)
            self.tk_images_refs.append(tk_img)
        except: self.lbl_orig_img.config(image='', text="Erreur Image")

        # --- 2. Affichage Crops (Droite) ---
        row, col = 0, 0
        # On réduit le nombre de colonnes car le panneau est moins large (2 ou 3 max)
        max_cols = 2 

        if not crop_files:
            ttk.Label(self.scrollable_frame, text="AUCUN CROP").pack(pady=20)
        else:
            # On configure les colonnes de la grille pour qu'elles se centrent
            self.scrollable_frame.grid_columnconfigure(0, weight=1)
            self.scrollable_frame.grid_columnconfigure(1, weight=1)

            for c_file in crop_files:
                try:
                    f = ttk.Frame(self.scrollable_frame, borderwidth=1, relief="solid")
                    f.grid(row=row, column=col, padx=10, pady=10) # Pas de sticky pour centrer la boite

                    # Image Crop
                    img_c = Image.open(os.path.join(self.crops_path, c_file))
                    img_c = ImageOps.contain(img_c, (200, 200))
                    tk_ic = ImageTk.PhotoImage(img_c)
                    self.tk_images_refs.append(tk_ic)

                    lbl_img = ttk.Label(f, image=tk_ic)
                    lbl_img.pack()
                    
                    # Tag
                    tag_text = self.tags_dict.get(c_file, "???")
                    lbl_tag = ttk.Label(f, text=tag_text, font=("Arial", 14, "bold"), foreground="#0055ff")
                    lbl_tag.pack(pady=(5, 0))

                    # Nom Fichier
                    clean_name = c_file.replace(os.path.splitext(orig_filename)[0], "")
                    lbl_name = ttk.Label(f, text=clean_name, font=("Arial", 8), foreground="#555")
                    lbl_name.pack(pady=(0, 5))

                    col += 1
                    if col >= max_cols:
                        col = 0; row += 1
                except: pass

    def next_image(self):
        if self.index < len(self.group_keys) - 1:
            self.index += 1
            self.show_current_group()

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.show_current_group()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBrowserApp(root, ORIGINALS_DIR, CROPS_DIR, TAGS_FILE)
    root.mainloop()