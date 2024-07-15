import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance
from collections import deque
import numpy as np

class TranslateDialog:
    def __init__(self, parent, callback):
        top = self.top = tk.Toplevel(parent)
        top.title("Transladar Imagem")
        top.configure(bg="#d8bfd8")

        self.callback = callback

        tk.Label(top, text="Deslocamento X:", bg="#d8bfd8").pack(pady=5)
        self.x_entry = tk.Entry(top)
        self.x_entry.pack(pady=5)

        tk.Label(top, text="Deslocamento Y:", bg="#d8bfd8").pack(pady=5)
        self.y_entry = tk.Entry(top)
        self.y_entry.pack(pady=5)

        tk.Button(top, text="Aplicar", command=self.apply).pack(pady=10)

    def apply(self):
        x = self.x_entry.get()
        y = self.y_entry.get()
        try:
            x = int(x)
            y = int(y)
            self.callback(x, y)
            self.top.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Deslocamento inválido!")

class ResizeDialog:
    def __init__(self, parent, callback):
        top = self.top = tk.Toplevel(parent)
        top.title("Redimensionar Imagem")
        top.configure(bg="#d8bfd8")

        self.callback = callback

        tk.Label(top, text="Nova Largura:", bg="#d8bfd8").pack(pady=5)
        self.width_entry = tk.Entry(top)
        self.width_entry.pack(pady=5)

        tk.Label(top, text="Nova Altura:", bg="#d8bfd8").pack(pady=5)
        self.height_entry = tk.Entry(top)
        self.height_entry.pack(pady=5)

        tk.Button(top, text="Aplicar", command=self.apply).pack(pady=10)

    def apply(self):
        width = self.width_entry.get()
        height = self.height_entry.get()
        try:
            width = int(width)
            height = int(height)
            self.callback(width, height)
            self.top.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Dimensões inválidas!")

class ImageEditorApp:
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1080
    DISPLAY_WIDTH = 480
    DISPLAY_HEIGHT = 640

    def __init__(self, root):
        self.root = root
        self.configure_root()
        self.create_widgets()

        self.original_image = None
        self.editable_image = None
        self.undo_stack = deque(maxlen=10)

    def configure_root(self):
        self.root.title("Editor de Imagens Avançado")
        self.root.configure(bg="#d8bfd8")
        self.root.state('zoomed')
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", self.close_app)

    def create_widgets(self):
        self.title_font = ("Helvetica", 16, "bold")
        self.button_font = ("Helvetica", 12)
        
        self.main_frame = tk.Frame(self.root, bg="#d8bfd8")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.create_image_frames()
        self.create_control_buttons()
        self.create_option_buttons()

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

    def create_image_frames(self):
        self.original_frame = tk.Frame(self.main_frame, bg="#ffffff", padx=5, pady=5)
        self.original_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.original_img_label = tk.Label(self.original_frame, text="Imagem Original", bg="#ffffff", font=self.title_font)
        self.original_img_label.pack(side=tk.TOP, padx=5, pady=5)
        self.original_canvas = tk.Canvas(self.original_frame, bg="#ffffff", width=self.DISPLAY_WIDTH, height=self.DISPLAY_HEIGHT)
        self.original_canvas.pack(side=tk.TOP, padx=5, pady=5)

        self.editable_frame = tk.Frame(self.main_frame, bg="#ffffff", padx=5, pady=5)
        self.editable_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.editable_img_label = tk.Label(self.editable_frame, text="Imagem Editada", bg="#ffffff", font=self.title_font)
        self.editable_img_label.pack(side=tk.TOP, padx=5, pady=5)
        self.editable_canvas = tk.Canvas(self.editable_frame, bg="#ffffff", width=self.DISPLAY_WIDTH, height=self.DISPLAY_HEIGHT)
        self.editable_canvas.pack(side=tk.TOP, padx=5, pady=5)

        self.image_size_label = tk.Label(self.main_frame, text="Tamanho da Imagem: ", bg="#d8bfd8", font=("Helvetica", 12), fg="black")
        self.image_size_label.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    def create_control_buttons(self):
        self.button_frame_left = tk.Frame(self.main_frame, bg="#d8bfd8")
        self.button_frame_left.grid(row=3, column=0, sticky="w", padx=10, pady=10)

        self.button_frame_right = tk.Frame(self.main_frame, bg="#d8bfd8")
        self.button_frame_right.grid(row=3, column=1, sticky="e", padx=10, pady=10)

        self.load_reset_frame = tk.Frame(self.main_frame, bg="#d8bfd8")
        self.load_reset_frame.grid(row=2, column=0, columnspan=2, sticky="we", padx=10, pady=10)

        self.create_button("Carregar Imagem", self.load_image, parent_frame=self.button_frame_left, side=tk.LEFT)
        self.create_button("Salvar Imagem", self.save_image, parent_frame=self.button_frame_left, side=tk.LEFT)
        self.create_button("Resetar", self.reset_image, parent_frame=self.button_frame_right, side=tk.RIGHT)
        self.create_button("Matriz", self.show_matrix_info, parent_frame=self.button_frame_right, side=tk.RIGHT)

    def create_option_buttons(self):
        self.option_button_frame = tk.Frame(self.main_frame, bg="#d8bfd8")
        self.option_button_frame.grid(row=4, column=0, columnspan=2, sticky="we", padx=10, pady=10)

        self.create_button("Rotacionar 90°", lambda: self.transform_image("rotate_90"), self.option_button_frame)
        self.create_button("Inverter Horizontal", lambda: self.transform_image("flip_horizontal"), self.option_button_frame)
        self.create_button("Inverter Vertical", lambda: self.transform_image("flip_vertical"), self.option_button_frame)
        self.create_button("Preto e Branco", lambda: self.transform_image("bw"), self.option_button_frame)
        self.create_button("Filtro de Saturação", lambda: self.transform_image("saturate"), self.option_button_frame)
        self.create_button("Filtro Negativo", self.apply_negative_filter, self.option_button_frame)
        self.create_button("Transladar", self.open_translate_dialog, self.option_button_frame)
        self.create_button("Redimensionar", self.open_resize_dialog_editable, self.option_button_frame)

    def create_button(self, text, command, parent_frame=None, side=tk.LEFT):
        frame = parent_frame if parent_frame else self.button_frame_left

        btn = tk.Button(frame, text=text, command=command, bg="#f0f0f0", fg="black", font=self.button_font,
                padx=10, pady=5, bd=2, relief="flat", cursor="hand2")

        btn.pack(side=side, padx=5, pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            original_image = Image.open(file_path)
            if original_image.width > self.MAX_WIDTH or original_image.height > self.MAX_HEIGHT:
                original_image.thumbnail((self.MAX_WIDTH, self.MAX_HEIGHT))
            self.original_image = original_image.copy()
            self.editable_image = original_image.copy()
            self.update_images()

    def update_images(self):
        if self.original_image:
            original_photo = ImageTk.PhotoImage(self.original_image)
            self.original_canvas.create_image(0, 0, anchor=tk.NW, image=original_photo)
            self.original_canvas.image = original_photo

        if self.editable_image:
            edited_photo = ImageTk.PhotoImage(self.editable_image)
            self.editable_canvas.create_image(0, 0, anchor=tk.NW, image=edited_photo)
            self.editable_canvas.image = edited_photo
            self.image_size_label.config(text=f"Tamanho da Imagem: {self.editable_image.width}x{self.editable_image.height}")
        else:
            self.image_size_label.config(text="Tamanho da Imagem: ")

    def transform_image(self, action):
        if self.editable_image:
            if not self.undo_stack:
                self.undo_stack.append(self.editable_image.copy())
            if action == "rotate_90":
                self.editable_image = self.editable_image.rotate(90, expand=True)
            elif action == "flip_horizontal":
                self.editable_image = ImageOps.mirror(self.editable_image)
            elif action == "flip_vertical":
                self.editable_image = ImageOps.flip(self.editable_image)
            elif action == "bw":
                self.editable_image = self.editable_image.convert("1")  # Convertendo para imagem binária (preto e branco)
            elif action == "saturate":
                enhancer = ImageEnhance.Color(self.editable_image)
                self.editable_image = enhancer.enhance(2)
            self.update_images()
            self.undo_stack.append(self.editable_image.copy())
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada!")

    def apply_negative_filter(self):
        if self.editable_image:
            self.editable_image = ImageOps.invert(self.editable_image.convert('RGB'))
            self.update_images()
            self.undo_stack.append(self.editable_image.copy())
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada!")

    def open_translate_dialog(self):
        if self.editable_image:
            dialog = TranslateDialog(self.root, self.translate_image_dialog)
            self.root.wait_window(dialog.top)
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada!")

    def translate_image_dialog(self, x, y):
        if x is not None and y is not None:
            if self.editable_image:
                original_editable_image = self.editable_image.copy()
                translated = Image.new("RGB", self.editable_image.size)
                translated.paste(original_editable_image, (int(x), int(y)))
                self.editable_image = translated
                self.update_images()
                self.undo_stack.append(original_editable_image)
            else:
                messagebox.showerror("Erro", "Nenhuma imagem carregada!")

    def open_resize_dialog_editable(self):
        if self.editable_image:
            dialog = ResizeDialog(self.root, self.resize_image_editable)
            self.root.wait_window(dialog.top)
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada!")

    def resize_image_editable(self, width, height):
        if width and height:
            new_width = int(width)
            new_height = int(height)
            if new_width > 0 and new_height > 0:
                original_editable_image = self.editable_image.copy()
                self.editable_image = self.editable_image.resize((new_width, new_height))
                self.update_images()
                self.undo_stack.append(original_editable_image)
            else:
                messagebox.showerror("Erro", "Dimensões inválidas!")
        else:
            messagebox.showerror("Erro", "Dimensões inválidas!")

    def reset_image(self):
        if self.original_image:
            self.editable_image = self.original_image.copy()
            self.update_images()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada!")

    def save_image(self):
        if self.editable_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if file_path:
                self.editable_image.save(file_path)
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada!")

    def close_app(self, event=None):
        self.root.quit()

    def show_matrix_info(self):
        if self.editable_image:
            image_array = np.array(self.editable_image)

            matrix_window = tk.Toplevel(self.root)
            matrix_window.title("Matriz da Imagem")
            matrix_window.configure(bg="#d8bfd8")
            matrix_window.geometry("550x500")

            matrix_info = (
                "Uma matriz é uma estrutura de dados bidimensional composta por linhas e colunas. "
                "Na computação gráfica, uma imagem pode ser representada como uma matriz, "
                "onde cada elemento da matriz representa um pixel da imagem. "
                "Os valores contidos na matriz determinam a intensidade das cores vermelha, verde e azul "
                "(no caso de imagens RGB) ou a intensidade do cinza (no caso de imagens em escala de cinza).\n\n"
                f"Matriz da imagem editada ({image_array.shape[0]} linhas x {image_array.shape[1]} colunas):\n"
            )

            matrix_label = tk.Label(matrix_window, text=matrix_info, bg="#d8bfd8", justify=tk.LEFT)
            matrix_label.pack(padx=10, pady=10)

            matrix_text = tk.Text(matrix_window, wrap=tk.WORD, bg="#ffffff", font=("Courier New", 10))
            matrix_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

            # Função para resumir a matriz em uma versão 3x3
            def get_resized_matrix(matrix, size=3):
                rows, cols = matrix.shape[0], matrix.shape[1]
                row_indices = np.linspace(0, rows - 1, size, dtype=int)
                col_indices = np.linspace(0, cols - 1, size, dtype=int)
                return matrix[np.ix_(row_indices, col_indices)]

            resized_matrix = get_resized_matrix(image_array, 3)

            for row in resized_matrix:
                row_text = ' '.join(map(str, row))
                matrix_text.insert(tk.END, row_text + '\n')

            matrix_text.insert(tk.END, "\n(Esta é uma versão resumida da matriz 3x3.)")
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()
