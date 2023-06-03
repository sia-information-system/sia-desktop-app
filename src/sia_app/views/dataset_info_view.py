import tkinter as tk
import ttkbootstrap as ttk
from sia_app.views.templates.scrollable_view import ScrollableView
import sia_app.utils.dataset_utils as dataset_utils
import sia_app.utils.general_utils as gen_utils
import sia_app.utils.basic_form_fields as form_fields
import sia_app.utils.global_variables as global_vars
import sia_app.utils.project_manager as prj_mgmt
from siaplotlib.processing import wrangling as plot_wrangling

class DatasetInfoView(ScrollableView):
  def __init__(self, master, root_app_window):
    super().__init__(master)
    self.root_window = root_app_window # Main window. Used to change views.

    self.dimensions_list = dataset_utils.get_dimensions()
    self.variable_list = dataset_utils.get_variables()

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    # ------------------ Elements of the view  ------------------

    view_title_label = ttk.Label(self.scroll_frame, text='Información del conjunto de datos', font=('Helvetica', 14))
    view_title_label.pack(pady=10)

    columns_frame = ttk.Frame(self.scroll_frame)
    columns_frame.pack(fill='both', expand=1, padx=30)

    # Column 1

    info_frame = ttk.Frame(columns_frame)
    info_frame.pack(side='left', fill='y', expand=1)

    title_label = ttk.Label(info_frame, text='Metadatos', font=('Helvetica', 14))
    title_label.pack(pady=10)

    info_text = ttk.Text(info_frame, wrap='word', font=('Helvetica', 10))
    info_text.pack(fill='both', expand=1, pady=20)

    info_text.insert('end', dataset_utils.get_dataset_info())
    info_text.configure(state='disabled')
    # Widget is resized to have a height equal to the number of text rows in the widget.
    info_text.configure(height=info_text.index('end-1c').split('.')[0])

    # Column 2
    set_dim_vars_frame = ttk.Frame(columns_frame)
    set_dim_vars_frame.pack(side='left', fill='both', expand=1)

    title_col2_label = ttk.Label(set_dim_vars_frame, text='Configuración de dimensiones y variables', font=('Helvetica', 14))
    title_col2_label.pack(pady=10)

    # Form.
    form_frame = ttk.Frame(set_dim_vars_frame)
    form_frame.pack(fill='x', padx=20, pady=10)

    label_text = 'Con apoyo de la información de la columna Metadatos por favor '
    label_text += 'indique que nombre es usado para cada dimensión y variable.'
    instructions_label = ttk.Label(form_frame, text=label_text)
    instructions_label.pack(fill='x', expand=1, pady=10)

    form_entries_frame = ttk.Frame(form_frame)
    form_entries_frame.pack(fill='x')

    self.dimensions_list = dataset_utils.get_dimensions()
    self.variable_list = dataset_utils.get_variables()

    dimensions_lblframe = ttk.Labelframe(form_entries_frame, text='Dimensiones')
    dimensions_lblframe.pack(fill='x', padx=10, pady=10)
    # Inner frame to add padding to the comboboxes.
    dimensions_frame = ttk.Frame(dimensions_lblframe)
    dimensions_frame.pack(fill='x', padx=20, pady=10)

    label_text = 'Tiempo:'
    options = self.dimensions_list + ['No definido']
    time_dim_cb = form_fields.create_combobox_row(dimensions_frame, label_text, options, label_width=35, entry_width=60)

    label_text = 'Profundidad:'
    options = self.dimensions_list + ['No definido']
    depth_dim_cb = form_fields.create_combobox_row(dimensions_frame, label_text, options, label_width=35, entry_width=60)

    label_text = 'Longitud:'
    options = self.dimensions_list + ['No definido']
    lon_dim_cb = form_fields.create_combobox_row(dimensions_frame, label_text, options, label_width=35, entry_width=60)

    label_text = 'Latitud:'
    options = self.dimensions_list + ['No definido']
    lat_dim_cb = form_fields.create_combobox_row(dimensions_frame, label_text, options, label_width=35, entry_width=60)

    variables_lbl_frame = ttk.Labelframe(form_entries_frame, text='Variables')
    variables_lbl_frame.pack(fill='x', padx=10, pady=10)
    # Inner frame to add padding to the comboboxes.
    variables_frame = ttk.Frame(variables_lbl_frame)
    variables_frame.pack(fill='x', padx=20, pady=10)

    label_text = 'Velocidad hacia el norte (corrientes):'
    options = self.variable_list + ['No definido']
    northward_var_cb = form_fields.create_combobox_row(variables_frame, label_text, options, label_width=35, entry_width=60)

    label_text = 'Velocidad hacia el este (corrientes):'
    options = self.variable_list + ['No definido']
    eastward_var_cb = form_fields.create_combobox_row(variables_frame, label_text, options, label_width=35, entry_width=60)

    # Save configuration button.
    save_data_button = ttk.Button(
      form_frame, 
      text='Guardar configuración', 
      command=lambda: self.__save_configuration(
        time_dim_cb.get(),
        depth_dim_cb.get(),
        lon_dim_cb.get(),
        lat_dim_cb.get(),
        northward_var_cb.get(),
        eastward_var_cb.get()
      )
    )
    save_data_button.pack(pady=10)

    if gen_utils.is_project_loaded():
      if gen_utils.is_project_configured():
        time_dim_cb.set(global_vars.time_dim)
        depth_dim_cb.set(global_vars.depth_dim)
        lon_dim_cb.set(global_vars.lon_dim)
        lat_dim_cb.set(global_vars.lat_dim)
        northward_var_cb.set(global_vars.northward_var)
        eastward_var_cb.set(global_vars.eastward_var)
    else:
      time_dim_cb.configure(state='disabled')
      depth_dim_cb.configure(state='disabled')
      lon_dim_cb.configure(state='disabled')
      lat_dim_cb.configure(state='disabled')
      northward_var_cb.configure(state='disabled')
      eastward_var_cb.configure(state='disabled')
      save_data_button.configure(state='disabled')
    
  def __save_configuration(self, time_dim, depth_dim, lon_dim, lat_dim, northward_var, eastward_var):

    valid_fields = self.__fields_validation(time_dim, depth_dim, lon_dim, lat_dim, northward_var, eastward_var)
    if not valid_fields: 
      return

    # Save in global variables.
    global_vars.time_dim = time_dim
    global_vars.depth_dim = depth_dim
    global_vars.lon_dim = lon_dim
    global_vars.lat_dim = lat_dim
    global_vars.northward_var = northward_var
    global_vars.eastward_var = eastward_var

    project_path = global_vars.current_project_path
    prj_mgmt.save_dataset_config(project_path, time_dim, depth_dim, lon_dim, lat_dim, northward_var, eastward_var)

    if global_vars.northward_var != None and global_vars.northward_var != 'No definido' and \
      global_vars.eastward_var != None and global_vars.eastward_var != 'No definido':
      single_vel_var_name = 'current_velocity'
      # Calculate unique velocity and load to project dataset
      plot_wrangling.calc_unique_velocity(
        dataset=global_vars.current_project_dataset,
        eastward_var_name=global_vars.eastward_var,
        northward_var_name=global_vars.northward_var,
        unique_velocity_name=single_vel_var_name
      )

    # Reload workspace view in main window.
    workspace_view = gen_utils.find_view(self.root_window, 'WorkspaceView')
    gen_utils.change_view(self.root_window, workspace_view)

    tk.messagebox.showinfo(title='Información', message='Configuración guardada correctamente.')

  def __fields_validation(self, time_dim, depth_dim, lon_dim, lat_dim, northward_var, eastward_var):
    empty_fields = []
    if time_dim == '': empty_fields.append('Dimensión Tiempo')
    if depth_dim == '': empty_fields.append('Dimensión Profundidad')
    if lon_dim == '': empty_fields.append('Dimensión Longitud')
    if lat_dim == '': empty_fields.append('Dimensión Latitud')
    if northward_var == '': empty_fields.append('Variable Velocidad hacia el norte')
    if eastward_var == '': empty_fields.append('Variable Velocidad hacia el este')

    if len(empty_fields) > 0:
      message = 'Todos los campos son obligatorios. Datos faltantes: \n'
      message += ', '.join(empty_fields)
      tk.messagebox.showerror(title='Error', message=message)
      return False

    return True
