import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk, ImageOps
import numpy as np


class ImageEditorApp:
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1080
    DISPLAY_WIDTH = 600
    DISPLAY_HEIGHT = 320

    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Imagens Avançado")
        self.root.configure(bg="#003c5f")

        title_font = ("Helvetica", 16, "bold")

        self.main_frame = tk.Frame(root, bg="#003c5f")
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        self.original_frame = tk.Frame(
            self.main_frame, bg="#ffffff", padx=10, pady=10, borderwidth=1, relief="solid")
        self.original_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.original_img_label = tk.Label(
            self.original_frame, text="Imagem Original", bg="#ffffff", font=title_font)
        self.original_img_label.grid(row=0, column=0, padx=10, pady=5)
        self.original_img_widget = tk.Label(self.original_frame, bg="#ffffff")
        self.original_img_widget.grid(row=1, column=0, padx=10, pady=5)

        self.editable_frame = tk.Frame(
            self.main_frame, bg="#ffffff", padx=10, pady=10, borderwidth=1, relief="solid")
        self.editable_frame.grid(
            row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.editable_img_label = tk.Label(
            self.editable_frame, text="Imagem Editável", bg="#ffffff", font=title_font)
        self.editable_img_label.grid(row=0, column=0, padx=10, pady=5)
        self.editable_img_widget = tk.Label(self.editable_frame, bg="#ffffff")
        self.editable_img_widget.grid(row=1, column=0, padx=10, pady=5)

        self.image_size_label = tk.Label(
            self.main_frame, text="Tamanho da Imagem: ", bg="#0f79ba", font=("Helvetica", 12))
        self.image_size_label.grid(
            row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.button_frame = tk.Frame(self.main_frame, bg="#0f79ba")
        self.button_frame.grid(row=2, column=0, columnspan=2,
                               sticky="we", padx=10, pady=10)

        self.create_button("Carregar Imagem", self.load_image, side=tk.LEFT)
        self.create_button("Resetar", self.reset_image, side=tk.RIGHT)

        self.option_button_frame = tk.Frame(self.main_frame, bg="#0f79ba")
        self.option_button_frame.grid(
            row=3, column=0, columnspan=2, sticky="we", padx=10, pady=10)

        self.create_button("Rotacionar 90°", lambda: self.transform_image(
            "rotate_90"), self.option_button_frame)
        self.create_button("Inverter Horizontal", lambda: self.transform_image(
            "flip_horizontal"), self.option_button_frame)
        self.create_button("Inverter Vertical", lambda: self.transform_image(
            "flip_vertical"), self.option_button_frame)
        self.create_button("Preto e Branco", lambda: self.transform_image(
            "bw"), self.option_button_frame)
        self.create_button("Transladar", self.translate_image,
                           self.option_button_frame)
        self.create_button("Redimensionar", self.resize_image,
                           self.option_button_frame)
        self.create_button("Salvar Imagem", self.save_image,
                           self.option_button_frame)

        self.original_image = None
        self.image = None

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

    def create_button(self, text, command, parent_frame=None, side=tk.LEFT):
        frame = parent_frame if parent_frame else self.button_frame
        btn = tk.Button(frame, text=text, command=command, bg="#0f79ba", fg="#ffffff", font=(
            "Helvetica", 12), padx=10, pady=5, bd=0, relief="flat", highlightthickness=0, cursor="hand2", borderwidth=3)
        btn.pack(side=side, padx=5, pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            original_image = Image.open(file_path)
            # Redimensionar a imagem original para se ajustar ao tamanho do quadro disponível
            original_image.thumbnail((self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
            self.original_image = original_image.copy()
            self.image = self.original_image.copy()
            self.update_images()

    def update_images(self):
        # Obter as dimensões do quadro em que as imagens serão exibidas
        frame_width = self.DISPLAY_WIDTH
        frame_height = self.DISPLAY_HEIGHT

        # Redimensionar a imagem original e a imagem editada para se ajustarem ao tamanho do quadro
        original_image_resized = self.original_image.resize((frame_width, frame_height))
        edited_image_resized = self.image.resize((frame_width, frame_height))

        # Converter as imagens para o formato PhotoImage
        self.original_photo = ImageTk.PhotoImage(original_image_resized)
        self.photo = ImageTk.PhotoImage(edited_image_resized)

        # Configurar os widgets de imagem para exibir as imagens redimensionadas
        self.original_img_widget.config(image=self.original_photo)
        self.editable_img_widget.config(image=self.photo)

        # Atualizar a label que exibe o tamanho da imagem
        if self.image:
            self.image_size_label.config(text=f"Tamanho da Imagem: {frame_width}x{frame_height}")
        else:
            self.image_size_label.config(text="Tamanho da Imagem: ")

    def transform_image(self, action):
        if self.image:
            if action == "rotate_90":
                self.image = self.image.rotate(90, expand=True)
            elif action == "flip_horizontal":
                self.image = ImageOps.mirror(self.image)
            elif action == "flip_vertical":
                self.image = ImageOps.flip(self.image)
            elif action == "bw":
                self.image = self.image.convert("L")
            self.update_images()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada!")

    def translate_image(self):
        if self.image:
            x = simpledialog.askinteger("Transladar", "X offset:", parent=self.root)
            y = simpledialog.askinteger("Transladar", "Y offset:", parent=self.root)
            if x is not None and y is not None:
                # Crie uma nova imagem do mesmo tamanho que a imagem original
                translated = Image.new("RGB", self.image.size)
                # Cole a imagem original na nova imagem com o deslocamento (x, y)
                translated.paste(self.image, (x, y))
                self.image = translated
                self.update_images()

    def resize_image(self):
        if self.image:
            width = simpledialog.askinteger(
                "Redimensionar", "Nova largura:", parent=self.root)
            height = simpledialog.askinteger(
                "Redimensionar", "Nova altura:", parent=self.root)
            if width is not None and height is not None:
                img_array = np.array(self.image)
                resized_img_array = np.array(Image.fromarray(
                    img_array).resize((width, height)))
                self.image = Image.fromarray(resized_img_array)
                self.update_images()

    def reset_image(self):
        if self.original_image:
            self.image = self.original_image.copy()
            self.update_images()

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[(
                "PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
            if file_path:
                self.image.save(file_path)
        else:
            messagebox.showerror("Erro", "Nenhuma imagem para salvar!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
