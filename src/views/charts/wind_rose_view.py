import pathlib
import re
import sys
import tkinter as tk
import ttkbootstrap as ttk
import utils.dataset_utils as dataset_utils
import utils.general_utils as gen_utils
import utils.global_variables as global_vars
import utils.basic_form_fields as form_fields
import utils.project_manager as prj_mgmt
from datetime import datetime
from views.templates.tab_view import TabView
from siaplotlib.chart_building import level_chart
from siaplotlib.processing import computations
from siaplotlib.processing import wrangling

class WindRoseView(TabView):
  def __init__(self, master, project_path, worksheet_name):
    super().__init__(master, chart_type='WIND_ROSE')
    self.project_path = project_path
    self.worksheet_name = worksheet_name

    self.depth_list = dataset_utils.get_depth_values()
    self.dataset_lon_values = dataset_utils.get_longitude_values()
    self.dataset_lat_values = dataset_utils.get_latitude_values()
    speed = computations.calc_spd(
      dataset= global_vars.current_project_dataset,
      eastward_var_name = self.eastward_var,
      northward_var_name = self.northward_var
    )
    speed = wrangling.drop_nan(dataset = speed)
    self.dataset_min_speed = gen_utils.round_ceil(speed.min(), decimals=4)
    self.dataset_max_speed = gen_utils.round_floor(speed.max(), decimals=4)

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

    min_dataset_lon, max_dataset_lon = min(self.dataset_lon_values), max(self.dataset_lon_values)
    min_dataset_lat, max_dataset_lat = min(self.dataset_lat_values), max(self.dataset_lat_values)

    label_text = 'Longitud mínima:'
    self.lon_min_entry = form_fields.create_entry_row(form_entries_frame, label_text)
    self.lon_min_entry.insert(0, min_dataset_lon)

    label_text = 'Longitud máxima:'
    self.lon_max_entry = form_fields.create_entry_row(form_entries_frame, label_text)
    self.lon_max_entry.insert(0, max_dataset_lon)

    label_text = 'Latitud mínima:'
    self.lat_min_entry = form_fields.create_entry_row(form_entries_frame, label_text)
    self.lat_min_entry.insert(0, min_dataset_lat)

    label_text = 'Latitud máxima:'
    self.lat_max_entry = form_fields.create_entry_row(form_entries_frame, label_text)
    self.lat_max_entry.insert(0, max_dataset_lat)

    label_text = 'Cantidad de sectores:'
    self.n_sectors_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Velocidad mínima:'
    self.min_speed_legend_entry = form_fields.create_entry_row(form_entries_frame, label_text)
    self.min_speed_legend_entry.insert(0, self.dataset_min_speed)

    label_text = 'Velocidad máxima:'
    self.max_speed_legend_entry = form_fields.create_entry_row(form_entries_frame, label_text)
    self.max_speed_legend_entry.insert(0, self.dataset_max_speed)

    label_text = 'Salto en la velocidad:'
    self.speed_legend_step_entry = form_fields.create_entry_row(form_entries_frame, label_text)
    self.speed_legend_step_entry.insert(0, 0.2)

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
        self.n_sectors_entry.get(),
        self.min_speed_legend_entry.get(),
        self.max_speed_legend_entry.get(),
        self.speed_legend_step_entry.get(),
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
    n_sectors,
    min_speed_legend, 
    max_speed_legend, 
    speed_legend_step
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
    print(f'min_speed_legend: "{min_speed_legend}"', file=sys.stderr)
    print(f'max_speed_legend: "{max_speed_legend}"', file=sys.stderr)
    print(f'speed_legend_step: "{speed_legend_step}"', file=sys.stderr)

    # Hide column 2 with the chart and buttons.
    self.chart_and_btns_frame.pack_forget()
    # Validations.
    valid_fields = self.__fields_validation(depth, chart_title, target_date, palette_colors,
      lon_min, lon_max, lat_min, lat_max, n_sectors, min_speed_legend, max_speed_legend, speed_legend_step)
    if not valid_fields:
      return
    # Start progress bar.
    self.__start_progress_bar()

    try:
      self.__generate_static_chart(depth, chart_title, target_date, palette_colors, 
        lon_min, lon_max, lat_min, lat_max, n_sectors, min_speed_legend, max_speed_legend, speed_legend_step)
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
    n_sectors,
    min_speed_legend,
    max_speed_legend,
    speed_legend_step
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

    bin_min = float(min_speed_legend) # 1 
    bin_max = float(max_speed_legend) # 2
    bin_jmp = float(speed_legend_step) # 0.2

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
    n_sectors,
    min_speed_legend,
    max_speed_legend,
    speed_legend_step
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
    if min_speed_legend == '': empty_fields.append('Velocidad mínima')
    if max_speed_legend == '': empty_fields.append('Velocidad máxima')
    if speed_legend_step == '': empty_fields.append('Salto de la velocidad')

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

      min_dataset_lon, max_dataset_lon = min(self.dataset_lon_values), max(self.dataset_lon_values)
      min_dataset_lat, max_dataset_lat = min(self.dataset_lat_values), max(self.dataset_lat_values)

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

    # Validation of the speed legend range and step.
    try:
      try:
        min_speed_legend = float(min_speed_legend)
        max_speed_legend = float(max_speed_legend)
        speed_legend_step = float(speed_legend_step)
      except:
        raise Exception('La velocidad mínima, máxima y el salto deben ser números flotantes.')

      if min_speed_legend >= max_speed_legend:
        raise Exception('La velocidad mínima debe ser menor a la velocidad máxima.')

      if min_speed_legend < self.dataset_min_speed or max_speed_legend > self.dataset_max_speed:
        message = 'La velocidad mínima y máxima deben estar dentro del rango del dataset.\n'
        message += f'Rango de velocidad: {self.dataset_min_speed} a {self.dataset_max_speed}.'
        raise Exception(message)

      speed_diff = max_speed_legend - min_speed_legend
      if speed_legend_step <= 0 or speed_legend_step > speed_diff:
        message = 'El salto de la velocidad debe estar entre 0 y la diferencia entre '
        message += f'la velocidad máxima y mínima, cuyo valor es {speed_diff}.'
        raise Exception(message)
    except Exception as err:
      tk.messagebox.showerror(title='Error', message=err)
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
      'n_sectors': self.n_sectors_entry.get(),
      'min_speed_legend': self.min_speed_legend_entry.get(),
      'max_speed_legend': self.max_speed_legend_entry.get(),
      'speed_legend_step': self.speed_legend_step_entry.get()
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
      self.lon_min_entry.delete(0, 'end')
      self.lon_min_entry.insert(0, parameters['lon_min'])
      self.lon_max_entry.delete(0, 'end')
      self.lon_max_entry.insert(0, parameters['lon_max'])
      self.lat_min_entry.delete(0, 'end')
      self.lat_min_entry.insert(0, parameters['lat_min'])
      self.lat_max_entry.delete(0, 'end')
      self.lat_max_entry.insert(0, parameters['lat_max'])
      self.n_sectors_entry.insert(0, parameters['n_sectors'])
      self.min_speed_legend_entry.delete(0, 'end')
      self.min_speed_legend_entry.insert(0, parameters['min_speed_legend'])
      self.max_speed_legend_entry.delete(0, 'end')
      self.max_speed_legend_entry.insert(0, parameters['max_speed_legend'])
      self.speed_legend_step_entry.delete(0, 'end')
      self.speed_legend_step_entry.insert(0, parameters['speed_legend_step'])

      img_path = pathlib.Path(global_vars.current_project_path, chart_img_rel_path)
      self.show_static_chart_img(img_path)