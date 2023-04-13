import textwrap
import string
import ttkbootstrap as ttk
import utils.general_utils as gen_utils
import utils.global_variables as global_vars
import utils.project_manager as prj_mgmt
from tkinter import messagebox
from ttkbootstrap.dialogs.dialogs import QueryDialog, Messagebox
from views.charts.heatmap_view import HeatMapView
from views.charts.contour_map_view import ContourMapView
from views.charts.single_point_time_series_view import SinglePointTimeSeriesView
from views.charts.currents_views import CurrentsChartView
from views.charts.wind_rose_view import WindRoseView
from views.charts.single_point_vertical_profile_view import SinglePointVerticalProfileView
from views.charts.vertical_slice_view import VerticalSliceView

# Docs for QueryDialog: https://ttkbootstrap.readthedocs.io/en/latest/api/dialogs/querydialog/
class NewSheetDialogBox(QueryDialog):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.chart_type_cb = None # Combobox widget for chart type.
    self.chart_type_cb_result = None # Value of the combobox widget.
    self.proceed_to_add = False
    self.chart_type_dict = {
      'Mapa de calor': 'HEATMAP',
      'Curva de nivel': 'CONTOUR_MAP',
      'Serie de tiempo': 'TIME_SERIES',
      'Gráfica de corrientes': 'CURRENTS_CHART',
      'Rosa de los vientos': 'WIND_ROSE',
      'Perfil vertical': 'VERTICAL_PROFILE',
      'Corte vertical': 'VERTICAL_SLICE',
    }

  def create_body(self, master):
    '''Override. Adds the form section.'''
    self.proceed_to_add = False

    form_frame = ttk.Frame(master, padding=self._padding)
    if self._prompt:
      for p in self._prompt.split('\n'):
        prompt = '\n'.join(textwrap.wrap(p, width=self._width))
        prompt_label = ttk.Label(form_frame, text=prompt)
        prompt_label.pack(pady=(0, 20), anchor='n')

    entry_label = ttk.Label(form_frame, text='Nombre de la hoja:')
    entry_label.pack(pady=(0, 5), fill='x', anchor='n')
    name_entry = ttk.Entry(master=form_frame)
    name_entry.insert('end', self._initialvalue)
    name_entry.pack(pady=(0, 10), fill='x')
    name_entry.bind('<Return>', self.on_submit)
    name_entry.bind('<KP_Enter>', self.on_submit)
    name_entry.bind('<Escape>', self.on_cancel)

    combobox_label = ttk.Label(form_frame, text='Tipo de visualización:')
    combobox_label.pack(pady=(0, 5), fill='x', anchor='n')
    chart_types = list(self.chart_type_dict.keys())
    chart_type_cb = ttk.Combobox(form_frame, values=chart_types, state='readonly')
    chart_type_cb.pack(fill='both', pady=(10, 0))
    chart_type_cb.pack(pady=(0, 10), fill='x')
    chart_type_cb.bind('<Return>', self.on_submit)
    chart_type_cb.bind('<KP_Enter>', self.on_submit)
    chart_type_cb.bind('<Escape>', self.on_cancel)

    form_frame.pack(fill='x', expand=1)
    self._initial_focus = name_entry
    self.chart_type_cb = chart_type_cb

  def on_submit(self, *_):
    '''Override. Save result, destroy the toplevel, and apply any post-hoc data manipulations.'''
    self._result = self._initial_focus.get() # Entry worksheet name.
    self.chart_type_cb_result = self.chart_type_cb.get()

    # Validate data.
    valid_result = self.validate()
    if not valid_result:
        return  # keep toplevel open for valid response

    self._toplevel.destroy()
    self.apply()
    self.proceed_to_add = True

  def validate(self):
    ''' overridde
    Validate the data
    This method is called automatically to validate the data before
    the dialog is destroyed. Can be subclassed and overridden.
    '''

    if self._result == '':
      Messagebox.ok(
        message='Asegurese de ingresar un nombre para la hoja',
        title='Datos faltantes',
        parent=self._toplevel
      )
      return False

    worksheet_exists = prj_mgmt.worksheet_exists(
      sheet_name=self._result, 
      project_path=global_vars.current_project_path
    )
    if worksheet_exists:
      Messagebox.ok(
        message='Ya existe una hoja con ese nombre, ingrese otro.',
        title='Datos duplicados',
        parent=self._toplevel
      )
      return False

    if self.chart_type_cb_result == '':
      Messagebox.ok(
        message='Asegurese de seleccionar un tipo de visualización',
        title='Datos faltantes',
        parent=self._toplevel
      )
      return False

    # Valid result
    return True

  def create_buttonbox(self, master):
    '''Overrides the parent method; adds the message buttonbox'''
    frame = ttk.Frame(master, padding=(5, 10))

    submit = ttk.Button(
      master=frame,
      bootstyle='primary',
      text='Crear',
      command=self.on_submit,
    )
    submit.pack(padx=5, side='right')
    submit.lower()  # set focus traversal left-to-right

    cancel = ttk.Button(
      master=frame,
      bootstyle='secondary',
      text='Cancelar',
      command=self.on_cancel,
    )
    cancel.pack(padx=5, side='right')
    cancel.lower()  # set focus traversal left-to-right

    ttk.Separator(self._toplevel).pack(fill='x')
    frame.pack(side='bottom', fill='x', anchor='s')

  def get_sheet_data(self):
    return {
      'proceed_to_add': self.proceed_to_add,
      'name': self._result, 
      'chart_type': self.chart_type_dict[self.chart_type_cb_result] if self.proceed_to_add else None
    }


class WorkspaceView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)
    self.root_window = master # Main window. Used to change views.

    self.project_path = None
    self.project_dataset = None
    self.notebook = None

  def load_view(self):
    self.pack(fill='both', expand=1) # Load view frame.

    # Load current project path and current dataset
    self.project_path = global_vars.current_project_path
    self.project_dataset = global_vars.current_project_dataset

    project_name = prj_mgmt.get_project_name(project_path=self.project_path)
    title = 'Proyecto: ' + string.capwords(project_name)
    project_title_label = ttk.Label(self, text=title, font=('TkDefaultFont', 14))
    project_title_label.pack(pady=10)

    if not self.project_dataset:
      self.__create_empty_project_frame()
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
      chart_frame = CurrentsChartView(self.notebook)
    elif chart_type == 'WIND_ROSE':
      chart_frame = WindRoseView(self.notebook)
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

  def __create_empty_project_frame(self):
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

  def __redirect_to_create_project(self):
    new_project_view = gen_utils.find_view(self.root_window, 'NewProjectView')
    gen_utils.change_view(self.root_window, new_project_view)
