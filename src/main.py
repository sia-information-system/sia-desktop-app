import tkinter as tk
import ttkbootstrap as ttk
import pathlib
import utils.general_utils as gen_utils
import utils.project_manager as prj_mgmt
from views.home_view import HomeView
from views.new_project_view import NewProjectView
from views.workspace_view import WorkspaceView
from views.dataset_info_view import DatasetInfoView
from views.data_extractor_view import DataExtractorView
from views.user_manual_view import UserManualView
from utils.global_constants import ASSETS_DIR

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
    self.data_extractor_view = DataExtractorView(self.window)
    self.user_manual_view = UserManualView(self.window)

    # Menu bar.
    self.__menu_bar = tk.Menu(self.window)
    self.__create_menu_bar()

    # Popup where is show DatasetInfoView.
    self.data_info_popup_window = None

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
    # file_menu.add_command(label='Cambiar fuente de datos', command=lambda: print('Cambiar fuente de datos'))
    file_menu.add_separator()
    file_menu.add_command(label='Salir', command=self.__on_close_app)

    # Create 'Espacio de trabajo' menu option.
    workspace_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Espacio de trabajo', command=lambda: gen_utils.change_view(self.window, self.workspace_view))

    # Create 'Información de datos' menu option.
    dataset_info_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Información de datos', command=self.__open_dataset_info_view_popup)

    # Create 'Extracción de datos' menu option.
    data_extractor_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Extracción de datos', command=lambda: gen_utils.change_view(self.window, self.data_extractor_view))

    # Create 'Manual de usuario' menu option.
    user_manual_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Manual de usuario', command=lambda: gen_utils.change_view(self.window, self.user_manual_view))

  def __on_close_app(self):
    if tk.messagebox.askokcancel('Salir', '¿Quieres salir de la aplicación?'):
      self.window.quit()

  def __open_dataset_info_view_popup(self):
    # If the popup window is not open, create it.
    if self.data_info_popup_window is None:
      self.data_info_popup_window = tk.Toplevel()
      self.data_info_popup_window.title('Información del conjunto de datos')

      # Get screen dimensions
      screen_width = self.data_info_popup_window.winfo_screenwidth()
      screen_height = self.data_info_popup_window.winfo_screenheight()
      # Calculate desired size of the popup window
      popup_width = int(screen_width * 0.9)  # 90% of screen width
      popup_height = int(screen_height * 0.8)  # 80% of screen height
      # Set the dimensions of the popup window
      self.data_info_popup_window.geometry(f"{popup_width}x{popup_height}+{int(screen_width*0.05)}+{int(screen_height*0.1)}")

      dataset_info_view = DatasetInfoView(self.data_info_popup_window, self.window)
      dataset_info_view.load_view()

      # When the popup window is closed, set the reference to None.
      self.data_info_popup_window.protocol('WM_DELETE_WINDOW', self.__close_dataset_info_view_popup)

    # If the popup window is already open, just show it, do not create a new one.
    else:
      self.data_info_popup_window.deiconify()

  def __close_dataset_info_view_popup(self):
    self.data_info_popup_window.destroy()
    self.data_info_popup_window = None

#  ------------------ Main ------------------

if __name__ == '__main__':
  window = ttk.Window(themename='cosmo')
  window.wm_state('zoomed')
  window.iconbitmap(pathlib.Path(ASSETS_DIR, 'images', 'sia-logo.ico'))
  app = App(window)
  window.mainloop()