import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
import pathlib
from utils.global_constants import ASSETS_DIR
from PIL import ImageTk, Image

class TabView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master, bootstyle='default')
    self.__col1_arrow_btn = None
    self.__arrow_label = None
    self.__col2_params = None
    self.col2_user_params = None
    self.col2_real_values = None
    self.col3_chart = None
    self.chart_img = None
    self.chart_img_label = None

  def load_view(self):
    self.columnconfigure(0, minsize=50)
    self.columnconfigure(1, weight=0)
    self.columnconfigure(2, weight=1)
    self.rowconfigure(0, weight=1)

    # Column 1
    self.__col1_arrow_btn = ttk.Frame(self, bootstyle='danger') # TODO: Delete bootstyle after testing.
    self.__col1_arrow_btn.grid(row=0, column=0, sticky='nsew')

    self.__arrow_label = ttk.Label(self.__col1_arrow_btn, text='⬅', font=('TkDefaultFont', 16))
    self.__arrow_label.pack(pady=10)
    self.__arrow_label.bind('<Button-1>', self.toggle_column)

    # Column 2
    self.__col2_params = ttk.Frame(self, bootstyle='info') # TODO: Delete bootstyle after testing.
    self.__col2_params.grid(row=0, column=1, sticky='nsew')

    params_notebook = ttk.Notebook(self.__col2_params, bootstyle='dark')
    params_notebook.pack(fill='both', expand=1, pady=10)

    self.col2_user_params = ttk.Frame(params_notebook)
    params_notebook.add(self.col2_user_params, text='Parametros')

    self.col2_real_values = ttk.Frame(params_notebook)
    params_notebook.add(self.col2_real_values, text='Información de la visualización')
    title_label = ttk.Label(self.col2_real_values, text='Valores reales de la visualización')
    title_label.pack(pady=20)

    # Column 3
    self.col3_chart = ttk.Frame(self, bootstyle='success') # TODO: Delete bootstyle after testing.
    self.col3_chart.grid(row=0, column=2, sticky='nsew')

    image_path = pathlib.Path(ASSETS_DIR, 'images', 'heatmap-example.png')
    self.chart_img = ImageTk.PhotoImage(Image.open(image_path))
    self.chart_img_label = ttk.Label(self.col3_chart, image=self.chart_img)
    self.chart_img_label.pack(pady=20)
    save_chart_btn = ttk.Button(self.col3_chart, text='Guardar gráfico', bootstyle='primary')
    save_chart_btn.pack(pady=20)

  def toggle_column(self, event):
    if self.__col2_params.winfo_ismapped():
      self.__col2_params.grid_remove()
      self.__arrow_label.configure(text='➡')
    else:
      self.__col2_params.grid(row=0, column=1, sticky='nsew')
      self.__arrow_label.configure(text='⬅')
