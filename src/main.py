import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from views.home_view import HomeView
from views.download_data_view import DownloadDataView
from views.visualizations_view import VisualizationsView
from views.downloaded_data_view import DownloadedDataView
from views.saved_charts_view import SavedChartsView

class App:
  def __init__(self, window):
    self.window = window
    self.title_app = 'Sistema de información geográfica para la extracción y análisis de datos oceanográficos'
    self.window.title(self.title_app)

    # App placed in center of screen.
    self.place_and_center_app(800, 500)

    # Create home view.
    self.home_view = HomeView(self.window, self.title_app)
    # Create main views ('windows') for each option in the menu bar.
    self.download_data_view = DownloadDataView(self.window)
    self.visualizations_view = VisualizationsView(self.window)
    self.downloaded_data_view = DownloadedDataView(self.window)
    self.saved_charts_view = SavedChartsView(self.window)

    # Menu bar.
    self.menu_bar = tk.Menu(self.window)
    self.create_menu_bar()

    self.load_view(self.home_view)

  def place_and_center_app(self, app_width, app_height):
    screen_width = self.window.winfo_screenwidth()
    screen_height = self.window.winfo_screenheight()
    # Top left corner (tlc) position.
    tlc_x = int( (screen_width / 2) - (app_width / 2) )
    tlc_y = int( (screen_height / 2) - (app_height / 2) )
    self.window.geometry(f'{app_width}x{app_height}+{tlc_x}+{tlc_y}')

  def load_view(self, view):
    self.clear_views()
    view.load_view()

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
    tools_menu.add_command(label='Descargar Datos', command=lambda: self.load_view(self.download_data_view))
    tools_menu.add_command(label='Visualizaciones', command=lambda: self.load_view(self.visualizations_view))

    # Create 'Historial' menu option.
    history_menu = tk.Menu(self.menu_bar, tearoff=False)
    self.menu_bar.add_cascade(label='Historial', menu=history_menu)
    history_menu.add_command(label='Datos descargados', command=lambda: self.load_view(self.downloaded_data_view))
    history_menu.add_command(label='Visualizaciones guardadas', command=lambda: self.load_view(self.saved_charts_view))

  def clear_view(self, view):
    # Destroy all widgets from view (frame), including inner widgets.
    for widget in view.winfo_children():
      widget.destroy()

    # Clear view, do not destroy the view (frame) itself just hide it.
    view.pack_forget()

  # Clear all main views that works as 'window' for each option in the menu bar.
  def clear_views(self):
    self.clear_view(self.home_view)
    self.clear_view(self.download_data_view)
    self.clear_view(self.visualizations_view)
    self.clear_view(self.downloaded_data_view)
    self.clear_view(self.saved_charts_view)

#  ------------------ Main ------------------

if __name__ == '__main__':
  window = ttk.Window(themename='cosmo')
  app = App(window)
  window.mainloop()