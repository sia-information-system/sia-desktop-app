import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from home_frame import HomeFrame
from download_data_frame import DownloadDataFrame
from visualizations_frame import VisualizationsFrame
from downloaded_data_frame import DownloadedDataFrame
from saved_charts_frame import SavedChartsFrame

class App:
  def __init__(self, window):
    self.window = window
    self.title_app = 'Sistema de información geográfica para la extracción y análisis de datos oceanográficos'
    self.window.title(self.title_app)

    # App placed in center of screen.
    self.place_and_center_app(800, 500)

    # Create home frame.
    self.home_frame = HomeFrame(self.window, self.title_app)
    # Create main frames ('windows') for each option in the menu bar.
    self.download_data_frame = DownloadDataFrame(self.window)
    self.visualizations_frame = VisualizationsFrame(self.window)
    self.downloaded_data_frame = DownloadedDataFrame(self.window)
    self.saved_charts_frame = SavedChartsFrame(self.window)

    # Menu bar.
    self.menu_bar = tk.Menu(self.window)
    self.create_menu_bar()

    self.load_frame(self.home_frame)

  def place_and_center_app(self, app_width, app_height):
    screen_width = self.window.winfo_screenwidth()
    screen_height = self.window.winfo_screenheight()
    # Top left corner (tlc) position.
    tlc_x = int( (screen_width / 2) - (app_width / 2) )
    tlc_y = int( (screen_height / 2) - (app_height / 2) )
    self.window.geometry(f'{app_width}x{app_height}+{tlc_x}+{tlc_y}')

  def load_frame(self, frame):
    self.clear_frames()
    frame.load_frame()

  def create_menu_bar(self):
    self.window.config(menu=self.menu_bar)

    # Create 'Archivo' menu option.
    file_menu = tk.Menu(self.menu_bar, tearoff=False)
    self.menu_bar.add_cascade(label='Archivo', menu=file_menu)
    file_menu.add_command(label='Nuevo', command=lambda: print('Nuevo archivo'))
    file_menu.add_separator()
    file_menu.add_command(label='Salir', command=self.window.quit)

    # Create 'Herramientas' menu option.
    tools_menu = tk.Menu(self.menu_bar, tearoff=False)
    self.menu_bar.add_cascade(label='Herramientas', menu=tools_menu)
    tools_menu.add_command(label='Descargar Datos', command=lambda: self.load_frame(self.download_data_frame))
    tools_menu.add_command(label='Visualizaciones', command=lambda: self.load_frame(self.visualizations_frame))

    # Create 'Historial' menu option.
    history_menu = tk.Menu(self.menu_bar, tearoff=False)
    self.menu_bar.add_cascade(label='Historial', menu=history_menu)
    history_menu.add_command(label='Datos descargados', command=lambda: self.load_frame(self.downloaded_data_frame))
    history_menu.add_command(label='Visualizaciones guardadas', command=lambda: self.load_frame(self.saved_charts_frame))

  def clear_frame(self, frame):
    # Destroy all widgets from frame, including inner frames.
    for widget in frame.winfo_children():
      widget.destroy()

    # Clear frame (do not destroy the frame itself, just hide it).
    frame.pack_forget()

  # Clear all main frames that works as 'window' for each option in the menu bar.
  def clear_frames(self):
    self.clear_frame(self.home_frame)
    self.clear_frame(self.download_data_frame)
    self.clear_frame(self.visualizations_frame)
    self.clear_frame(self.downloaded_data_frame)
    self.clear_frame(self.saved_charts_frame)

#  ------------------ Main ------------------

if __name__ == '__main__':
  window = ttk.Window(themename='cosmo')
  app = App(window)
  window.mainloop()