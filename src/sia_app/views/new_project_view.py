import tkinter as tk
import ttkbootstrap as ttk
import sia_app.utils.general_utils as gen_utils
import sia_app.utils.global_variables as global_vars
import sia_app.utils.project_manager as prj_mgmt
from tkinter.filedialog import askopenfilename
from sia_app.utils.global_constants import HOME_DATASETS_DIR

class NewProjectView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)
    self.root_window = master # Main window. Used to change views.

    self.__browse_btn = None # Button to select dataset file.
    self.__dataset_path = None

    # Variables for widgets.
    self.__get_data_option_var = ttk.StringVar() # Options: select_dataset, download_dataset
    self.__selected_dataset_label_var = ttk.StringVar()

  def load_view(self):
    self.pack(fill='both', expand=1)

    title_view_label = ttk.Label(self, text='Configuración del nuevo proyecto', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=10)

    # Set default values.
    self.__dataset_path = None
    self.__get_data_option_var.set('select_dataset')
    self.__selected_dataset_label_var.set('No se ha seleccionado ningún archivo.')

    # Form.
    form_frame = ttk.Frame(self, bootstyle='default')
    form_frame.pack(fill='x', padx=300, pady=20)

    form_entries_frame = ttk.Frame(form_frame)
    form_entries_frame.pack(fill='x')

    title_entry = self.__create_name_project_row(form_entries_frame)
    # Hidden until the option is implemented. # TODO:
    # self.__create_options_to_get_data_row(form_entries_frame)
    self.__create_select_dataset_row(form_entries_frame)

    # Create project button.
    create_project_button = ttk.Button(
      form_frame, 
      text='Crear proyecto', 
      command=lambda: self.__create_project(
        title_entry.get(), 
        self.__get_data_option_var.get(), 
        self.__dataset_path
      )
    )
    create_project_button.pack(pady=10)

  def __create_name_project_row(self, master):
    name_project_row = ttk.Frame(master)
    name_project_row.pack(fill='x', pady=10)

    label_text = 'Nombre del proyecto:'
    title_label = ttk.Label(name_project_row, text=label_text, width=30)
    title_label.pack(side='left')

    title_entry = ttk.Entry(name_project_row)
    title_entry.pack(side='left', fill='x', expand=1)

    return title_entry

  def __create_options_to_get_data_row(self, master):
    options_to_get_data_row = ttk.Frame(master)
    options_to_get_data_row.pack(fill='x', pady=10)

    label_text = 'Fuente de datos:'
    option_label = ttk.Label(options_to_get_data_row, text=label_text, width=30)
    option_label.pack(side='left')

    select_dataset_option = ttk.Radiobutton(
      master=options_to_get_data_row, 
      text='Seleccionar conjunto de datos', 
      variable=self.__get_data_option_var, 
      value='select_dataset',
      command = lambda : self.__set_browse_btn_state('normal')
    )
    select_dataset_option.pack(side='left')

    download_data_option = ttk.Radiobutton(
      master=options_to_get_data_row, 
      text='Descargar conjunto de datos', 
      variable=self.__get_data_option_var, 
      value='download_dataset',
      command = lambda : self.__set_browse_btn_state('disabled')
    )
    download_data_option.pack(side='left', padx=15)

  def __create_select_dataset_row(self, master):
    select_dataset_row = ttk.Frame(master)
    select_dataset_row.pack(fill='x', pady=10)

    label_text = 'Conjunto de datos:'
    title_label = ttk.Label(select_dataset_row, text=label_text, width=30)
    title_label.pack(side='left')

    self.__browse_btn = ttk.Button(
      master=select_dataset_row, 
      text='Buscar', 
      command=self.__on_browse, 
      width=8,
      bootstyle='dark', 
    )
    self.__browse_btn.pack(side='left')

    selected_dataset_label = ttk.Label(select_dataset_row, textvariable=self.__selected_dataset_label_var)
    selected_dataset_label.pack(side='left', padx=15)

  def __on_browse(self):
    '''Callback for directory browse'''
    self.__dataset_path = askopenfilename(
      title='Seleccione el conjunto de datos',
      initialdir=HOME_DATASETS_DIR
    )
    if self.__dataset_path:
      self.__selected_dataset_label_var.set('Archivo seleccionado.')

  def __set_browse_btn_state(self, new_state):
    if self.__browse_btn:
      self.__browse_btn['state'] = new_state

  def __create_project(self, project_name, get_data_option, selected_dataset):
    valid_fields = self.__fields_validation(project_name, get_data_option, selected_dataset)

    if not valid_fields:
      return

    # Create project.
    dataset = selected_dataset if get_data_option == 'select_dataset' else None
    global_vars.current_project_path = prj_mgmt.save_project(project_name, dataset)
    # Set current project dataset.
    if dataset:
      global_vars.current_project_dataset = prj_mgmt.get_dataset_project(global_vars.current_project_path)
    else:
      global_vars.current_project_dataset = None
    # Reset default values of dataset dimensiones and variables.
    global_vars.time_dim = None
    global_vars.depth_dim = None
    global_vars.lon_dim = None
    global_vars.lat_dim = None
    global_vars.northward_var = None
    global_vars.eastward_var = None

    # Redirect to the next view.
    if get_data_option == 'select_dataset':
      workspace_view = gen_utils.find_view(self.root_window, 'WorkspaceView')
      gen_utils.change_view(self.root_window, workspace_view)
    else:
      data_extractor_view = gen_utils.find_view(self.root_window, 'DataExtractorView')
      gen_utils.change_view(self.root_window, data_extractor_view)

  def __fields_validation(self, project_name, get_data_option, dataset_path):
    if not project_name:
      tk.messagebox.showerror(title='Error', message='Por favor escribe el nombre del proyecto.')
      return False

    if prj_mgmt.project_exists(project_name):
      tk.messagebox.showerror(title='Error', message='Ya existe un proyecto con ese nombre.')
      return False

    if get_data_option == 'select_dataset' and not dataset_path:
      tk.messagebox.showerror(title='Error', message='Por favor seleccione el conjunto de datos.')
      return False

    return True
    