import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
import pathlib
from utils.global_constants import ASSETS_DIR
import utils.global_variables as global_vars
from PIL import ImageTk, Image

class TabView(ttk.Frame):
  def __init__(self, master, chart_type):
    super().__init__(master, bootstyle='default')
    self.chart_type = chart_type

    self.time_dim = global_vars.time_dim
    self.depth_dim = global_vars.depth_dim
    self.lon_dim = global_vars.lon_dim
    self.lat_dim = global_vars.lat_dim
    self.northward_var = global_vars.northward_var
    self.eastward_var = global_vars.eastward_var

    self.__col1_arrow_btn = None
    self.__arrow_label = None
    self.__col2_params = None
    self.col2_user_params_frame = None
    self.col2_real_values_frame = None
    self.__col3_chart = None
    self.chart_and_btns_frame = None
    self.chart_img = None
    self.chart_img_label = None

    self.gif_images = []
    self.current_frame = 0
    self.num_frames = None
    self.play_chart_btn = None
    self.duration_unit = None
    self.duration = None

    self.chart_builder = None

  def load_view(self):
    self.columnconfigure(0, minsize=50)
    self.columnconfigure(1, weight=0)
    self.columnconfigure(2, weight=1)
    self.rowconfigure(0, weight=1)

    # Column 1
    self.__col1_arrow_btn = ttk.Frame(self, bootstyle='default') # TODO: Delete bootstyle after testing. danger
    self.__col1_arrow_btn.grid(row=0, column=0, sticky='nsew')

    self.__arrow_label = ttk.Label(self.__col1_arrow_btn, text='⬅', font=('TkDefaultFont', 16))
    self.__arrow_label.pack(pady=10)
    self.__arrow_label.bind('<Button-1>', self.__toggle_column)

    # Column 2
    self.__col2_params = ScrolledFrame(self, bootstyle='default', width=500) # TODO: Delete bootstyle after testing. info
    self.__col2_params.grid(row=0, column=1, sticky='nsew')

    params_notebook = ttk.Notebook(self.__col2_params, bootstyle='dark')
    params_notebook.pack(fill='both', expand=1, padx=(0, 20), pady=10) # Different padx because of the scrollbar

    self.col2_user_params_frame = ttk.Frame(params_notebook)
    params_notebook.add(self.col2_user_params_frame, text='Parametros')

    self.col2_real_values_frame = ttk.Frame(params_notebook)
    params_notebook.add(self.col2_real_values_frame, text='Información de la visualización')
    title_label = ttk.Label(self.col2_real_values_frame, text='Valores reales de la visualización')
    title_label.pack(pady=20)

    # Column 3
    self.__col3_chart = ScrolledFrame(self, bootstyle='default') # TODO: Delete bootstyle after testing. success
    self.__col3_chart.grid(row=0, column=2, sticky='nsew')

    col3_chart_title = ttk.Label(self.__col3_chart, text='Gráfica', font=('TkDefaultFont', 14))
    col3_chart_title.pack(pady=(10, 0))

    self.chart_and_btns_frame = ttk.Frame(self.__col3_chart)
    self.chart_and_btns_frame.pack(fill='both', expand=1)

    example_chart_img_path = None
    if self.chart_type == 'HEATMAP':
      example_chart_img_path = pathlib.Path(ASSETS_DIR, 'images', 'heatmap-example.png')
    elif self.chart_type == 'CONTOUR_MAP':
      example_chart_img_path = pathlib.Path(ASSETS_DIR, 'images', 'contourmap-example.png')
    elif self.chart_type == 'TIME_SERIES':
      example_chart_img_path = pathlib.Path(ASSETS_DIR, 'images', 'time-series-example.png')
    elif self.chart_type == 'CURRENTS_CHART':
      example_chart_img_path = pathlib.Path(ASSETS_DIR, 'images', 'currents-chart-example.png')
    elif self.chart_type == 'WIND_ROSE':
      example_chart_img_path = pathlib.Path(ASSETS_DIR, 'images', 'windrose-example.png')
    else:
      example_chart_img_path = pathlib.Path(ASSETS_DIR, 'images', 'heatmap-example.png')

    img = Image.open(example_chart_img_path)
    img_resized = self.resize_chart_img(img)
    self.chart_img = ImageTk.PhotoImage(img_resized)
    self.chart_img_label = ttk.Label(self.chart_and_btns_frame, image=self.chart_img)
    self.chart_img_label.pack(pady=(10, 0))

    save_chart_btn = ttk.Button(
      self.chart_and_btns_frame, 
      text='Guardar gráfico', 
      command=self.__save_chart,
      width=20,
      bootstyle='primary'
    )
    save_chart_btn.pack(pady=(10, 10))
    self.play_chart_btn = ttk.Button(
      self.chart_and_btns_frame, 
      text='Reproducir gráfico',
      command=self.__start_gif,
      width=20,
      bootstyle='success'
    )

  def get_gif_frames(self, gif_buffer):
    frames = []
    with Image.open(gif_buffer) as im:
      try:
        while True:
          frames.append(im.copy())
          im.seek(len(frames))  # Skip to next frame
      except EOFError:
        pass  # End of frames

    # Convert PIL Image objects to PhotoImage objects
    return [ImageTk.PhotoImage(frame) for frame in frames]

  def resize_chart_img(self, chart_img):
    max_height = 600 # TODO: Tamaño adecudo creo que 500
    original_width, original_height = chart_img.size
    new_width = int(original_width * max_height / original_height)
    return chart_img.resize((new_width, max_height), Image.ANTIALIAS)

  def dataset_dims_and_vars_validation(self):
    # Check one dimension is enough to validate if dimensions and variables are configured.
    if not self.time_dim:
      message = 'Antes de continuar debe configurar los nombres de las dimensiones y variables '
      message += 'que usa el dataset. Para ello, por favor vaya a la pestaña "Información de datos"'
      message += ' y llene el formulario.\n'
      message += 'Este paso solo se le pedirá hacerlo una vez. Disculpe las molestias.'
      tk.messagebox.showerror(title='Dimensiones y variables no configuradas', message=message)
      return False

    return True

  def __toggle_column(self, event):
    if self.__col2_params.winfo_ismapped():
      self.__col2_params.grid_remove()
      self.__arrow_label.configure(text='➡')
    else:
      self.__col2_params.grid(row=0, column=1, sticky='nsew')
      self.__arrow_label.configure(text='⬅')

  def __start_gif(self):
    self.play_chart_btn['state'] = 'disabled'
    self.__play_gif()
  
  def __play_gif(self):
    # Update image label with current frame.
    self.chart_img = self.gif_images[self.current_frame]
    self.chart_img_label.configure(image=self.chart_img)
    # Update current frame.
    self.current_frame = (self.current_frame + 1)
    if self.current_frame >= self.num_frames:
      self.current_frame = 0
      self.play_chart_btn['state'] = 'normal'
      return

    if self.duration_unit == 'SECONDS_PER_FRAME':
      gif_frame_duration_ms = round(self.duration * 1000)
    elif self.duration_unit == 'FRAMES_PER_SECOND':
      gif_frame_duration_ms = round(1000 / self.duration)

    # Recursive.
    self.after(gif_frame_duration_ms, self.__play_gif)

  def __save_chart(self):
    # Avoid save examples charts.
    if not self.chart_builder:
      return

    file_path = tk.filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('Archivos PNG', '*.png'), ('Archivos GIF', '*.gif')])
    if not file_path:
      return

    extension = pathlib.Path(file_path).suffix
    extension = extension.lower()
    if extension not in ['.png', '.gif']:
      tk.messagebox.showerror(title='Error', message='El archivo debe ser de tipo PNG o GIF.')
      return

    self.chart_builder.save(pathlib.Path(file_path))
    tk.messagebox.showinfo(title='Información', message='La gráfica se guardo con éxito.')
