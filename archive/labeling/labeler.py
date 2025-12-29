import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from crop_tag import crop_folder
from PIL import PngImagePlugin

# Global variables
image_files = []
current_image_index = 0
output_file = "user_inputs.txt"

def select_folder():
    global image_files, current_image_index
    folder_path = filedialog.askdirectory()
    if folder_path:
        crop_folder('labeling/best.pt', folder_path, "cropped_output")
        image_files = [os.path.join("cropped_output", f) for f in os.listdir("cropped_output") if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        current_image_index = 0
        if image_files:
            display_image()

def display_image():
    global current_image_index, image_files
    if current_image_index < len(image_files):
        file_path = image_files[current_image_index]
        pil_image = Image.open(file_path)
        pil_image.thumbnail((600, 400))
        tk_image = ImageTk.PhotoImage(pil_image)
        image_label.config(image=tk_image)
        image_label.image = tk_image
    else:
        image_label.config(image=None)
        image_label.image = None
        tk.messagebox.showinfo("Info", "Toutes les images ont été traitées.")

def save_input_and_next():
    global current_image_index, image_files
    user_input = text_input.get()
    if current_image_index < len(image_files):
        with open(output_file, "a") as f:
            image_path = image_files[current_image_index]
            pil_image = Image.open(image_path)
            metadata = PngImagePlugin.PngInfo()
            metadata.add_text("tagValue", user_input)
            print(f"Image saved with metadata: {image_path}")
            pil_image.save(image_path, pnginfo=metadata)
        current_image_index += 1
        text_input.delete(0, tk.END)
        display_image()

# --- Main Window ---
window = tk.Tk()
window.title("Étiqueteur d'étiquette ;)")
window.geometry("700x550")

main_frame = tk.Frame(window, padx=15, pady=15)
main_frame.pack(expand=True)


folder_button = tk.Button(
    main_frame,
    text="Choisir le dossier d'images",
    command=select_folder
)
folder_button.pack(pady=10)
submit_button = tk.Button(
    main_frame,
    text="Sauvegarder et Suivant",
    command=save_input_and_next
)

window.bind('<Return>', lambda event: save_input_and_next())
image_label = tk.Label(main_frame)
image_label.pack(pady=10)


text_prompt_label = tk.Label(main_frame, text="Entrez la valeur:")
text_prompt_label.pack()
text_input = tk.Entry(main_frame, width=50, font=("Arial", 15))
text_input.pack(pady=5)
submit_button.pack(pady=(10, 0))
window.mainloop()