import ttkbootstrap as ttk
from utils.global_constants import VISUALIZATIONS_DIR

class VisualizationsView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)

  def load_view(self):
    self.pack(fill='both', expand=1)
    label = ttk.Label(self, text='Herramienta para visualizar datos')
    label.pack(pady=(50, 0))