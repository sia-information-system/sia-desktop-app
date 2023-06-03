import tkinter as tk
import ttkbootstrap as ttk
import pathlib
import sia_app.utils.general_utils as gen_utils
import sia_app.utils.project_manager as prj_mgmt
from sia_app.views.home_view import HomeView
from sia_app.views.new_project_view import NewProjectView
from sia_app.views.workspace_view import WorkspaceView
from sia_app.views.dataset_info_view import DatasetInfoView
from sia_app.views.data_extractor_view import DataExtractorView
from sia_app.views.user_manual_view import UserManualView, LinksToDocsView
from sia_app.views.about_app_view import AboutAppView
from sia_app.utils.global_constants import ASSETS_DIR

class App:
  def __init__(self, window):
    self.window = window
    self.window.protocol('WM_DELETE_WINDOW', self.__on_close_app)
    self.title_app = 'Sistema de Información Ambiental'
    self.window.title(self.title_app)

    # App placed in center of screen.
    self.__center_window(self.window, 1024, 768)

    # Create home view.
    self.home_view = HomeView(self.window, self.title_app)
    # Create main views ('windows') for each option in the menu bar that required a window.
    self.new_project_view = NewProjectView(self.window)
    self.workspace_view = WorkspaceView(self.window)
    # self.data_extractor_view = DataExtractorView(self.window)

    # Menu bar.
    self.__menu_bar = tk.Menu(self.window)
    self.__create_menu_bar()

    # Popups windows.
    self.data_info_popup_window = None
    self.about_app_popup_window = None
    self.user_manual_popup_window = None
    self.data_extractor_popup_window = None

    gen_utils.change_view(self.window, self.home_view)

  def __center_window(self, window, window_width, window_height):
    screen_width = self.window.winfo_screenwidth()
    screen_height = self.window.winfo_screenheight()
    # Top left corner (tlc) position.
    tlc_x = int( (screen_width / 2) - (window_width / 2) )
    tlc_y = int( (screen_height / 2) - (window_height / 2) )

    window.geometry(f'{window_width}x{window_height}+{tlc_x}+{tlc_y}')

  def __center_window_with_percentajes(self, window, window_width_per=90, window_height_per=80):
    # Get screen dimensions
    screen_width = self.window.winfo_screenwidth()
    screen_height = self.window.winfo_screenheight()
    # Calculate desired size of the popup window
    popup_width = int(screen_width * window_width_per / 100)  # % of screen width
    popup_height = int(screen_height * window_height_per / 100)  # % of screen height
    # Set the dimensions of the popup window
    half_remaining_width = int(screen_width * (((100-window_width_per) / 100) / 2))
    half_remaining_height = int(screen_height * (((100-window_height_per) / 100) / 2))
    window.geometry(f'{popup_width}x{popup_height}+{half_remaining_width}+{half_remaining_height}')

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
    # self.__menu_bar.add_command(label='Extracción de datos', command=lambda: gen_utils.change_view(self.window, self.data_extractor_view))
    self.__menu_bar.add_command(label='Extracción de datos', command=self.__open_data_extractor_view_popup)

    # Create 'Manual de usuario' menu option.
    user_manual_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Documentación', command=self.__open_user_manual_view_popup)

    # Create 'Acerca de' menu option.
    about_menu = tk.Menu(self.__menu_bar, tearoff=False)
    self.__menu_bar.add_command(label='Acerca de', command=self.__open_about_app_view_popup)


  def __on_close_app(self):
    if tk.messagebox.askokcancel('Salir', '¿Quieres salir de la aplicación?'):
      self.window.quit()
  
  def __open_data_extractor_view_popup(self):
    # If the popup window is not open, create it.
    if self.data_extractor_popup_window is None:
      self.data_extractor_popup_window = tk.Toplevel()
      self.data_extractor_popup_window.title('Extracción de datos')
      self.__center_window_with_percentajes(self.data_extractor_popup_window, 90, 80)
      data_extractor_view = DataExtractorView(master=self.data_extractor_popup_window, root_app_window=self.window)
      data_extractor_view.load_view()
      self.data_extractor_popup_window.protocol('WM_DELETE_WINDOW', self.__close_data_extractor_view_popup)
    # If the popup window is already open, just show it, do not create a new one.
    else:
      self.data_extractor_popup_window.deiconify()

  def __close_data_extractor_view_popup(self):
    self.data_extractor_popup_window.destroy()
    self.data_extractor_popup_window = None

  def __open_dataset_info_view_popup(self):
    # If the popup window is not open, create it.
    if self.data_info_popup_window is None:
      self.data_info_popup_window = tk.Toplevel()
      self.data_info_popup_window.title('Información del conjunto de datos')
      self.__center_window_with_percentajes(self.data_info_popup_window, 90, 80)
      dataset_info_view = DatasetInfoView(self.data_info_popup_window, self.window)
      dataset_info_view.load_view()
      self.data_info_popup_window.protocol('WM_DELETE_WINDOW', self.__close_dataset_info_view_popup)
    # If the popup window is already open, just show it, do not create a new one.
    else:
      self.data_info_popup_window.deiconify()

  def __close_dataset_info_view_popup(self):
    self.data_info_popup_window.destroy()
    self.data_info_popup_window = None

  def __open_user_manual_view_popup(self):
    # If the popup window is not open, create it.
    if self.user_manual_popup_window is None:
      self.user_manual_popup_window = tk.Toplevel()
      self.user_manual_popup_window.title('Documentación y manual de usuario')
      # self.__center_window_with_percentajes(self.user_manual_popup_window, 90, 80)
      self.__center_window(self.user_manual_popup_window, 550, 300)
      # user_manual_view = UserManualView(self.user_manual_popup_window)
      user_manual_view = LinksToDocsView(self.user_manual_popup_window)
      user_manual_view.load_view()
      self.user_manual_popup_window.protocol('WM_DELETE_WINDOW', self.__close_user_manual_view_popup)
    # If the popup window is already open, just show it, do not create a new one.
    else:
      self.user_manual_popup_window.deiconify()

  def __close_user_manual_view_popup(self):
    self.user_manual_popup_window.destroy()
    self.user_manual_popup_window = None

  def __open_about_app_view_popup(self):
    # If the popup window is not open, create it.
    if self.about_app_popup_window is None:
      self.about_app_popup_window = tk.Toplevel()
      self.about_app_popup_window.title('Acerca de')
      self.__center_window(self.about_app_popup_window, 550, 400)
      about_app_view = AboutAppView(self.about_app_popup_window)
      about_app_view.load_view()
      self.about_app_popup_window.protocol('WM_DELETE_WINDOW', self.__close_about_app_view_popup)
    # If the popup window is already open, just show it, do not create a new one.
    else:
      self.about_app_popup_window.deiconify()

  def __close_about_app_view_popup(self):
    self.about_app_popup_window.destroy()
    self.about_app_popup_window = None

#  ------------------ Main ------------------


def main():
  window = ttk.Window(themename='cosmo')
  window.wm_state('zoomed')
  app = App(window)
  window.iconbitmap(pathlib.Path(ASSETS_DIR, 'images', 'sia-logo.ico'))
  window.mainloop()

if __name__ == '__main__':
  main()
