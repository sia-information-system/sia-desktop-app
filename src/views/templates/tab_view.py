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

    self.gif_images = []
    self.current_frame = 0
    self.num_frames = None
    self.play_chart_btn = None
    self.gif_frame_duration_ms = 1000 # miliseconds

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
    self.__col2_params = ttk.Frame(self, bootstyle='default') # TODO: Delete bootstyle after testing. info
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
    self.col3_chart = ttk.Frame(self, bootstyle='default') # TODO: Delete bootstyle after testing. success
    self.col3_chart.grid(row=0, column=2, sticky='nsew')

    image_path = pathlib.Path(ASSETS_DIR, 'images', 'heatmap-example.png')
    self.chart_img = ImageTk.PhotoImage(Image.open(image_path))
    self.chart_img_label = ttk.Label(self.col3_chart, image=self.chart_img)
    self.chart_img_label.pack(pady=20)
    save_chart_btn = ttk.Button(
      self.col3_chart, 
      text='Guardar gráfico', 
      width=20,
      bootstyle='primary'
    )
    save_chart_btn.pack(pady=(20, 10))
    self.play_chart_btn = ttk.Button(
      self.col3_chart, 
      text='Reproducir gráfico',
      command=self.__start_gif,
      width=20,
      bootstyle='success'
    )

  def load_gif_images(self, gif_path):
    print('Se llamo a load_gif_images')
    frames = []
    with Image.open(gif_path) as im:
      try:
        while True:
          frames.append(im.copy())
          im.seek(len(frames))  # Skip to next frame
      except EOFError:
        pass  # End of frames

    # Convert PIL Image objects to PhotoImage objects
    return [ImageTk.PhotoImage(frame) for frame in frames]

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

    # Recursive.
    self.after(self.gif_frame_duration_ms, self.__play_gif)

