import ttkbootstrap as ttk
import pathlib
from PIL import ImageTk, Image
from utils.global_constants import ASSETS_DIR
import utils.general_utils as gen_utils

class HomeView(ttk.Frame):
  def __init__(self, master, title_app):
    super().__init__(master)
    self.title_app = title_app
    self.logo_img = None

  def load_view(self):
    self.pack(fill='both', expand=1)

    name_app_label = ttk.Label(self, text=self.title_app, font=('Helvetica', 24, 'bold'))
    name_app_label.pack(pady=30)

    image_path = pathlib.Path(ASSETS_DIR, 'images', 'sia-logo.png')
    img = Image.open(image_path)
    img_resized = gen_utils.resize_chart_img(img, max_height=500)
    self.logo_img = ImageTk.PhotoImage(img_resized)
    logo_label = ttk.Label(self, image = self.logo_img)
    logo_label.pack(pady=(20,0))
