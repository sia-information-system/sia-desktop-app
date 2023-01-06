import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class DownloadedDataFrame(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)

  def load_frame(self):
    self.pack(fill='both', expand=1)
    label = ttk.Label(self, text='Datos descargados')
    label.pack(pady=60)