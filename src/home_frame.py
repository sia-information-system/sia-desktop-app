import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import ImageTk, Image

class HomeFrame(ttk.Frame):
  def __init__(self, master, title_app):
    super().__init__(master)
    self.title_app = title_app
    self.logo_img = None

  def load_frame(self):
    self.pack(fill='both', expand=1)

    self.logo_img = ImageTk.PhotoImage(Image.open('images/unicaribe_logo.png'))
    logo_label = ttk.Label(self, image = self.logo_img)
    logo_label.pack(pady=(80, 0))
    name_app_label = ttk.Label(self, text=self.title_app, font=('Helvetica', 14))
    name_app_label.pack(pady=20)