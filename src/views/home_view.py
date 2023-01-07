import ttkbootstrap as ttk
import pathlib
from PIL import ImageTk, Image
from utils.global_constants import ASSETS_DIR

class HomeView(ttk.Frame):
  def __init__(self, master, title_app):
    super().__init__(master)
    self.title_app = title_app
    self.logo_img = None

  def load_view(self):
    self.pack(fill='both', expand=1)
    image_path = pathlib.Path(ASSETS_DIR, 'images', 'unicaribe_logo.png')
    self.logo_img = ImageTk.PhotoImage(Image.open(image_path))
    logo_label = ttk.Label(self, image = self.logo_img)
    logo_label.pack(pady=(80, 0))
    name_app_label = ttk.Label(self, text=self.title_app, font=('Helvetica', 14))
    name_app_label.pack(pady=20)