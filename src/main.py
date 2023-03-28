import tkinter as tk
import ttkbootstrap as ttk
import utils.general_utils as gen_utils
import utils.project_manager as prj_mgmt
from views.home_view import HomeView
from views.new_project_view import NewProjectView
from views.workspace_view import WorkspaceView
from views.dataset_info_view import DatasetInfoView
from views.data_extractor_view import DataExtractorView
from views.user_manual_view import UserManualView

class App:
  def __init__(self, window):
    self.window = window
    self.window.protocol('WM_DELETE_WINDOW', self.__on_close_app)
    self.title_app = 'Sistema de Información Ambiental'
    self.window.title(self.title_app)

    # App placed in center of screen.
    self.__place_and_center_app(1024, 768)

    # Create home view.
    self.home_view = HomeView(self.window, self.title_app)
    # Create main views ('windows') for each option in the menu bar that required a window.
    self.new_project_view = NewProjectView(self.window)
    self.workspace_view = WorkspaceView(self.window)
    self.dataset_info_view = DatasetInfoView(self.window)
    self.data_extractor_view = DataExtractorView(self.window)
    self.user_manual_view = UserManualView(self.window)

    # Menu bar.
    self.__menu_bar = tk.Menu(self.window)
    self.__create_menu_bar()

    gen_utils.change_view(self.window, self.home_view)

  def __place_and_center_app(self, app_width, app_height):
    screen_width = self.window.winfo_screenwidth()
    screen_height = self.window.winfo_screenheight()
    # Top left corner (tlc) position.
    tlc_x = int( (screen_width / 2) - (app_width / 2) )
    tlc_y = int( (screen_height / 2) - (app_height / 2) )
    self.window.geometry(f'{app_width}x{app_height}+{tlc_x}+{tlc_y}')

  def __create_menu_bar(self):
    self.window.config(menu=self.__menu_bar)

    # Create 'Archivo' menu option.
    file_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_cascade(label='Archivo', menu=file_menu)
    file_menu.add_command(label='Nuevo Proyecto', command=lambda: gen_utils.change_view(self.window, self.new_project_view))
    file_menu.add_command(label='Abrir Proyecto', command=lambda: prj_mgmt.open_project(self.window))
    file_menu.add_command(label='Guardar', command=lambda: print('Guardar'))
    file_menu.add_command(label='Cambiar fuente de datos', command=lambda: print('Cambiar fuente de datos'))
    file_menu.add_separator()
    file_menu.add_command(label='Salir', command=self.__on_close_app)

    # Create 'Espacio de trabajo' menu option.
    workspace_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Espacio de trabajo', command=lambda: gen_utils.change_view(self.window, self.workspace_view))

    # Create 'Información de datos' menu option.
    dataset_info_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Información de datos', command=lambda: gen_utils.change_view(self.window, self.dataset_info_view))

    # Create 'Extracción de datos' menu option.
    data_extractor_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Extracción de datos', command=lambda: gen_utils.change_view(self.window, self.data_extractor_view))

    # Create 'Manual de usuario' menu option.
    user_manual_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Manual de usuario', command=lambda: gen_utils.change_view(self.window, self.user_manual_view))

  def __on_close_app(self):
    if tk.messagebox.askokcancel('Salir', '¿Quieres salir de la aplicación?'):
      self.window.quit()

#  ------------------ Main ------------------

if __name__ == '__main__':
  window = ttk.Window(themename='cosmo')
  window.wm_state('zoomed')
  app = App(window)
  window.mainloop()