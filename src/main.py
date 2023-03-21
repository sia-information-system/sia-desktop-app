import tkinter as tk
import ttkbootstrap as ttk
from tkinter.filedialog import askdirectory
from views.home_view import HomeView
from views.new_project_view import NewProjectView
from views.workspace_view import WorkspaceView
from views.dataset_info_view import DatasetInfoView
from views.data_extractor_view import DataExtractorView
from views.user_manual_view import UserManualView
from utils.general_utils import change_view
from utils.global_constants import HOME_PROJECTS_DIR
import utils.global_variables as global_vars
import utils.project_manager as prj_mgmt

class App:
  def __init__(self, window):
    self.window = window
    self.title_app = 'Oceanographic Information System'
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

    change_view(self.window, self.home_view)

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
    file_menu.add_command(label='Nuevo Proyecto', command=lambda: change_view(self.window, self.new_project_view))
    file_menu.add_command(label='Abrir Proyecto', command=self.__open_project)
    file_menu.add_command(label='Guardar', command=lambda: print('Guardar'))
    file_menu.add_command(label='Cambiar fuente de datos', command=lambda: print('Cambiar fuente de datos'))
    file_menu.add_separator()
    file_menu.add_command(label='Salir', command=self.window.quit)

    # Create 'Espacio de trabajo' menu option.
    workspace_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Espacio de trabajo', command=lambda: change_view(self.window, self.workspace_view))

    # Create 'Información de datos' menu option.
    dataset_info_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Información de datos', command=lambda: change_view(self.window, self.dataset_info_view))

    # Create 'Extracción de datos' menu option.
    data_extractor_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Extracción de datos', command=lambda: change_view(self.window, self.data_extractor_view))

    # Create 'Manual de usuario' menu option.
    user_manual_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Manual de usuario', command=lambda: change_view(self.window, self.user_manual_view))

  def __open_project(self):
    print('Open project')
    project_path = askdirectory(
      title='Selecciona el directorio del proyecto',
      initialdir=HOME_PROJECTS_DIR
    )
    print(f'Project path: {project_path}')
    global_vars.current_project_path = project_path
    global_vars.current_project_dataset = prj_mgmt.get_dataset_project(project_path)
    change_view(self.window, self.workspace_view)

#  ------------------ Main ------------------

if __name__ == '__main__':
  window = ttk.Window(themename='cosmo')
  app = App(window)
  window.mainloop()