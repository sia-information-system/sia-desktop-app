import ttkbootstrap as ttk

class SavedChartsView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)

  def load_view(self):
    self.pack(fill='both', expand=1)
    label = ttk.Label(self, text='Visualizaciones guardadas')
    label.pack(pady=80)