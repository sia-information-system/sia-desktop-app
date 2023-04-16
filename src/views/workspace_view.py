import string
import ttkbootstrap as ttk
import utils.general_utils as gen_utils
import utils.global_variables as global_vars
import utils.project_manager as prj_mgmt
from tkinter import messagebox
from widgets.own_widgets import NewSheetDialogBox
from views.charts.heatmap_view import HeatMapView
from views.charts.contour_map_view import ContourMapView
from views.charts.single_point_time_series_view import SinglePointTimeSeriesView
from views.charts.currents_views import CurrentsChartView
from views.charts.wind_rose_view import WindRoseView
from views.charts.single_point_vertical_profile_view import SinglePointVerticalProfileView
from views.charts.vertical_slice_view import VerticalSliceView

class WorkspaceView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)
    self.root_window = master # Main window. Used to change views.

    self.project_path = None
    self.notebook = None

  def load_view(self):
    self.pack(fill='both', expand=1) # Load view frame.

    # Load current project path.
    self.project_path = global_vars.current_project_path

    project_name = prj_mgmt.get_project_name(project_path=self.project_path)
    title = 'Proyecto: ' + string.capwords(project_name)
    project_title_label = ttk.Label(self, text=title, font=('TkDefaultFont', 14))
    project_title_label.pack(pady=10)

    if not gen_utils.is_project_loaded():
      self.__create_project_not_loaded_frame()
      return

    if not gen_utils.is_project_configured():
      self.__create_dataset_config_not_done_frame()
      return

    # Notebook.

    self.notebook = ttk.Notebook(self, bootstyle="secondary")
    self.notebook.pack(fill='both', expand=1, padx=20)
    self.__load_tabs_from_json(self.notebook, self.project_path)

    # Buttons.

    buttons_frame = ttk.Frame(self)
    buttons_frame.pack(pady=15)

    new_sheet_window = NewSheetDialogBox(prompt='Datos de la hoja de trabajo', parent=self)
    add_tab_button = ttk.Button(
      buttons_frame, 
      text='Nueva hoja', 
      command=lambda: self.__show_new_sheet_dialog(new_sheet_window),
      bootstyle='default',
      width=30
    )
    add_tab_button.pack(padx=(0, 10), side='left')

    remove_tab_button = ttk.Button(
      buttons_frame, 
      text='Eliminar hoja actual', 
      command=self.__remove_current_tab,
      bootstyle='danger',
      width=30
    )
    remove_tab_button.pack(padx=(10, 0), side='left')

  def __show_new_sheet_dialog(self, new_sheet_window):
    new_sheet_window.show()
    sheet_data = new_sheet_window.get_sheet_data()
    if sheet_data['proceed_to_add']:
      # Save worksheet to project.
      prj_mgmt.add_worksheet(self.project_path, sheet_data['name'], sheet_data['chart_type'])
      # Add tab to notebook.
      self.__add_tab(self.project_path, sheet_data['name'], sheet_data['chart_type'])

  def __add_tab(self, project_path, tab_name, chart_type):
    chart_frame = None
    if chart_type == 'HEATMAP':
      chart_frame = HeatMapView(self.notebook, project_path, tab_name)
    elif chart_type == 'CONTOUR_MAP':
      chart_frame = ContourMapView(self.notebook, project_path, tab_name)
    elif chart_type == 'TIME_SERIES':
      chart_frame = SinglePointTimeSeriesView(self.notebook, project_path, tab_name)
    elif chart_type == 'CURRENTS_CHART':
      chart_frame = CurrentsChartView(self.notebook, project_path, tab_name)
    elif chart_type == 'WIND_ROSE':
      chart_frame = WindRoseView(self.notebook, project_path, tab_name)
    elif chart_type == 'VERTICAL_PROFILE':
      chart_frame = SinglePointVerticalProfileView(self.notebook, project_path, tab_name)
    elif chart_type == 'VERTICAL_SLICE':
      chart_frame = VerticalSliceView(self.notebook, project_path, tab_name)

    chart_frame.load_view()

    result_add = self.notebook.add(chart_frame, text=tab_name)
    new_tab_index = self.notebook.index('end') - 1
    self.notebook.select(new_tab_index)

  def __remove_current_tab(self):
    tab_id = self.notebook.select()
    if not tab_id:
      return

    confirm_delete = messagebox.askyesno(
      title='Confirmación', 
      message='¿Quiere continuar con la eliminación de la hoja actual?', 
      icon=messagebox.WARNING
    )
    if not confirm_delete:
      return

    # Delete tab from json file.
    tab_info = self.notebook.tab(tab_id)
    tab_name = tab_info['text']
    prj_mgmt.delete_worksheet(self.project_path, tab_name)
    # Delete tab from notebook.
    self.notebook.forget(tab_id)

  def __load_tabs_from_json(self, notebook, project_path):
    worksheets = prj_mgmt.get_worksheets(project_path)
    for worksheet in worksheets:
      tab_name = worksheet['name']
      chart_type = worksheet['chart_type']
      self.__add_tab(project_path, tab_name, chart_type)

  def __create_project_not_loaded_frame(self):
    frame = ttk.Frame(self)
    frame.pack(fill='both', expand=1)

    label = ttk.Label(frame, text='No hay proyecto cargado.', font=('TkDefaultFont', 12))
    label.pack(pady=10)

    label = ttk.Label(frame, text='¿Desea crear o abrir uno?', font=('TkDefaultFont', 12))
    label.pack(pady=30)

    buttons_frame = ttk.Frame(frame)
    buttons_frame.pack(pady=10)

    create_project_button = ttk.Button(
      buttons_frame,
      text='Crear proyecto',
      command=self.__redirect_to_create_project,
      bootstyle='default',
      width=30
    )
    create_project_button.pack(pady=10, padx=(0, 10), side='left')

    open_project_button = ttk.Button(
      buttons_frame,
      text='Abrir proyecto',
      command=lambda: prj_mgmt.open_project(self.root_window),
      bootstyle='default',
      width=30
    )
    open_project_button.pack(pady=10, padx=(10, 0), side='left')

    return frame

  def __create_dataset_config_not_done_frame(self):
    frame = ttk.Frame(self)
    frame.pack(fill='both', expand=1)

    label = ttk.Label(frame, text='Configuracion del dataset no realizada.', font=('TkDefaultFont', 12))
    label.pack(pady=10)

    label_text = 'Antes de continuar debe configurar los nombres de las dimensiones y variables '
    label_text += 'que usa el dataset. \n\nPara ello, por favor vaya a la pestaña "Información de datos"'
    label_text += ' y llene el formulario.\n'
    label = ttk.Label(frame, text=label_text, font=('TkDefaultFont', 12))
    label.pack(pady=30)

    return frame

  def __redirect_to_create_project(self):
    new_project_view = gen_utils.find_view(self.root_window, 'NewProjectView')
    gen_utils.change_view(self.root_window, new_project_view)

