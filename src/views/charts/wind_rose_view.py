import pathlib
import re
import sys
import tkinter as tk
import ttkbootstrap as ttk
import utils.dataset_utils as dataset_utils
import utils.global_variables as global_vars
import utils.basic_form_fields as form_fields
import utils.project_manager as prj_mgmt
from datetime import datetime
from views.templates.tab_view import TabView
from siaplotlib.chart_building import level_chart

class WindRoseView(TabView):
  def __init__(self, master, project_path, worksheet_name):
    super().__init__(master, chart_type='WIND_ROSE')
    self.project_path = project_path
    self.worksheet_name = worksheet_name

    self.depth_list = dataset_utils.get_depth_values()

    self.__progress_bar = None

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    # ------------------ Elements of the view  ------------------

    title_view_label = ttk.Label(self.col2_user_params_frame, text='Rosa de los vientos', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=10)

    # Form.
    form_frame = ttk.Frame(self.col2_user_params_frame, bootstyle='default')
    form_frame.pack(fill='x', padx=20, pady=10)

    form_entries_frame = ttk.Frame(form_frame)
    form_entries_frame.pack(fill='x')

    label_text = 'Profundidad [m]:'
    default_depth = self.depth_list[0]
    self.depth_cb = form_fields.create_combobox_row(form_entries_frame, label_text, self.depth_list, default_option=default_depth)

    label_text = 'Título del gráfico:'
    self.chart_title_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Fecha objetivo:'
    self.target_date_entry = form_fields.create_date_entry_row(form_entries_frame, label_text)

    label_text = 'Paleta de colores:'
    palette_colors_list = ['OrRd', 'plasma', 'Greens', 'viridis']
    tooltip_text = 'Consultar Manual de usuario para más información sobre los codigos de los colores.'
    self.palette_colors_cb = form_fields.create_combobox_row(form_entries_frame, label_text, palette_colors_list, tooltip_text=tooltip_text)

    label_text = 'Longitud mínima:'
    self.lon_min_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Longitud máxima:'
    self.lon_max_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Latitud mínima:'
    self.lat_min_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Latitud máxima:'
    self.lat_max_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Cantidad de sectores:'
    self.n_sectors_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    # Restore previous values from the project file if was configured.
    self.__restore_params_and_img_if_apply()

    # Apply button.
    connect_button = ttk.Button(
      form_frame, 
      text='Generar gráfico', 
      command=lambda: self.__start_creation_chart(
        self.depth_cb.get(),
        self.chart_title_entry.get(),
        self.target_date_entry.entry.get(),
        self.palette_colors_cb.get(),
        self.lon_min_entry.get(), self.lon_max_entry.get(),
        self.lat_min_entry.get(), self.lat_max_entry.get(),
        self.n_sectors_entry.get()
      )
    )
    connect_button.pack(pady=10)

    self.__progress_bar = ttk.Progressbar(
      self.col2_user_params_frame,
      maximum=40, 
      mode='determinate',
      length=100,
      value=0,
      bootstyle='success striped'
    )
    self.__progress_bar.pack(pady=10)

  def __start_creation_chart(
    self,
    depth,
    chart_title,
    target_date,
    palette_colors,
    lon_min, lon_max,
    lat_min, lat_max,
    n_sectors
  ):
    print('-----------------------------', file=sys.stderr)
    print(f'depth: "{depth}"', file=sys.stderr)
    print(f'chart_title: "{chart_title}"', file=sys.stderr)
    print(f'target_date: "{target_date}"', file=sys.stderr)
    print(f'palette_colors: "{palette_colors}"', file=sys.stderr)
    print(f'lon_min: "{lon_min}"', file=sys.stderr)
    print(f'lon_max: "{lon_max}"', file=sys.stderr)
    print(f'lat_min: "{lat_min}"', file=sys.stderr)
    print(f'lat_max: "{lat_max}"', file=sys.stderr)
    print(f'n_sectors: "{n_sectors}"', file=sys.stderr)

    # Hide column 2 with the chart and buttons.
    self.chart_and_btns_frame.pack_forget()
    # Validations.
    dims_and_var_configured = self.dataset_dims_and_vars_validation()
    if not dims_and_var_configured:
      return
    valid_fields = self.__fields_validation(depth, chart_title, target_date, palette_colors,
      lon_min, lon_max, lat_min, lat_max, n_sectors)
    if not valid_fields:
      return
    # Start progress bar.
    self.__start_progress_bar()

    try:
      self.__generate_static_chart(depth, chart_title, target_date, palette_colors, 
        lon_min, lon_max, lat_min, lat_max, n_sectors)
    except Exception as err:
      self.__stop_progress_bar()
      tk.messagebox.showerror(title='Error', message=err)

  def __generate_static_chart(
    self,
    depth,
    chart_title,
    target_date,
    palette_colors,
    lon_min, lon_max,
    lat_min, lat_max,
    n_sectors
  ):
    print(f'-> Wind rose chart image.', file=sys.stderr)
    dataset = global_vars.current_project_dataset 
    lon_min, lon_max = float(lon_min), float(lon_max)
    lat_min, lat_max = float(lat_min), float(lat_max)

    dim_constraints = {
      self.time_dim: [target_date],
      self.depth_dim: depth,
      self.lon_dim: slice(lon_min, lon_max),
      self.lat_dim: slice(lat_min, lat_max),
    }

    # min, max, jumps
    bin_min = 1
    bin_max = 2
    bin_jmp = 0.2

    self.chart_builder = level_chart.StaticWindRoseBuilder(
      dataset=dataset,
      eastward_var_name=self.eastward_var,
      northward_var_name=self.northward_var,
      lat_dim_name=self.lat_dim,
      lon_dim_name=self.lon_dim,
      depth_dim_name=self.depth_dim,
      title=chart_title.strip(),
      bin_min=bin_min,
      bin_max=bin_max,
      bin_jmp=bin_jmp,
      color_palette=palette_colors,
      dim_constraints=dim_constraints,
      nsector=int(n_sectors)
    )
    self.chart_builder.build(
      success_callback=self.__static_success_build_callback, 
      failure_callback=self.__static_failure_build_callback
    )

  def __static_success_build_callback(self, chart_builder, subset):
    print(f'-> Image built.', file=sys.stderr)
    img_buffer = chart_builder._chart.get_buffer()
    self.show_static_chart_img(img_buffer)

    chart_img_rel_path = self.save_current_img_chart(self.worksheet_name, '.png')
    print(f'-> Static chart image saved in "{chart_img_rel_path}"', file=sys.stderr)
    self.__save_chart_parameters_and_img(chart_img_rel_path)
    print(f'-> Current state saved. Parameters and chart image', file=sys.stderr)

    self.__stop_progress_bar()
    self.chart_and_btns_frame.pack(fill='both', expand=1)

  def __static_failure_build_callback(self, err):
    print('--- An error ocurr while building the chart. ---', file=sys.stderr)
    print(err, file=sys.stderr)

    err_msg = 'Ocurrió un error al generar el gráfico.\n'
    err_msg += 'Revisa nuevamente los parámetros de creación del gráfico.'

    self.__stop_progress_bar()
    tk.messagebox.showerror(title='Error', message=err_msg)

  def __fields_validation(
    self, 
    depth, 
    chart_title,
    target_date,
    palette_colors,
    lon_min, lon_max,
    lat_min, lat_max,
    n_sectors
  ):
    chart_title = chart_title.strip()
    
    # Empty fields validation.
    empty_fields = []
    if chart_title == '': empty_fields.append('Título del gráfico')
    if depth == '': empty_fields.append('Profundidad')
    if target_date == '': empty_fields.append('Fecha objetivo')
    if palette_colors == '': empty_fields.append('Paleta de colores')
    if lon_min == '': empty_fields.append('Longitud mínima')
    if lon_max == '': empty_fields.append('Longitud máxima')
    if lat_min == '': empty_fields.append('Latitud mínima')
    if lat_max == '': empty_fields.append('Latitud máxima')
    if n_sectors == '': empty_fields.append('Número de sectores')

    if len(empty_fields) > 0:
      message = 'Todos los campos son obligatorios. Datos faltantes: \n'
      message += ', '.join(empty_fields)
      tk.messagebox.showerror(title='Error', message=message)
      return False

    # Validate target date format.
    try:
      target_date = datetime.strptime(target_date, '%Y-%m-%d')
    except:
      message = 'La fecha objetivo debe tener el formato "YYYY-MM-DD".'
      tk.messagebox.showerror(title='Error', message=message)
      return False

    # Validate minimun and maximum longitute and latitude range.
    try:
      try:
        lon_min, lon_max = float(lon_min), float(lon_max)
        lat_min, lat_max = float(lat_min), float(lat_max)
      except:
        raise Exception('La longitud y la latitud deben ser números flotantes.')

      if lon_min >= lon_max or lat_min >= lat_max:
        message = 'La longitud o latitud mínima debe ser menor a su valor máximo.'
        raise Exception(message)

      dataset_lon_values = dataset_utils.get_longitude_values()
      min_dataset_lon, max_dataset_lon = min(dataset_lon_values), max(dataset_lon_values)
      dataset_lat_values = dataset_utils.get_latitude_values()
      min_dataset_lat, max_dataset_lat = min(dataset_lat_values), max(dataset_lat_values)

      if lon_min < min_dataset_lon or lon_max > max_dataset_lon or \
        lat_min < min_dataset_lat or lat_max > max_dataset_lat:
        message = 'La longitud y latitud deben estar dentro del rango del dataset.\n'
        message += f'Rango de longitud: {min_dataset_lon}° a {max_dataset_lon}°.\n'
        message += f'Rango de latitud: {min_dataset_lat}° a {max_dataset_lat}°.'
        raise Exception(message)
    except Exception as err:
      tk.messagebox.showerror(title='Error', message=err)
      return False

    # Validate number of sectors.
    try:
      n_sectors = int(n_sectors)
      if n_sectors < 1:
        raise Exception()
    except:
      message = 'El número de sectores debe ser un número entero positivo.'
      tk.messagebox.showerror(title='Error', message=message)
      return False

    return True

  def __start_progress_bar(self):
    self.__progress_bar.start()

  def __stop_progress_bar(self):
    self.__progress_bar.stop()

  def __save_chart_parameters_and_img(self, chart_img_rel_path):
    parameters = {
      'depth': self.depth_cb.get(),
      'chart_title': self.chart_title_entry.get(),
      'target_date': self.target_date_entry.entry.get(),
      'palette_colors': self.palette_colors_cb.get(),
      'lon_min': self.lon_min_entry.get(),
      'lon_max': self.lon_max_entry.get(),
      'lat_min': self.lat_min_entry.get(),
      'lat_max': self.lat_max_entry.get(),
      'n_sectors': self.n_sectors_entry.get()
    }

    prj_mgmt.save_chart_parameters_and_img(self.project_path, self.worksheet_name, parameters, chart_img_rel_path)

  def __restore_params_and_img_if_apply(self):
    chart_data = prj_mgmt.get_chart_parameters_and_img(self.project_path, self.worksheet_name)
    parameters = chart_data['parameters']
    chart_img_rel_path = chart_data['chart_img_rel_path']

    if len(parameters) > 0:
      self.depth_cb.set(parameters['depth'])
      self.chart_title_entry.insert(0, parameters['chart_title'])
      self.target_date_entry.entry.delete(0, 'end')
      self.target_date_entry.entry.insert(0, parameters['target_date'])
      self.palette_colors_cb.set(parameters['palette_colors'])
      self.lon_min_entry.insert(0, parameters['lon_min'])
      self.lon_max_entry.insert(0, parameters['lon_max'])
      self.lat_min_entry.insert(0, parameters['lat_min'])
      self.lat_max_entry.insert(0, parameters['lat_max'])
      self.n_sectors_entry.insert(0, parameters['n_sectors'])

      img_path = pathlib.Path(global_vars.current_project_path, chart_img_rel_path)
      self.show_static_chart_img(img_path)