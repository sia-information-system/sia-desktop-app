import pathlib
import re
import sys
import tkinter as tk
import traceback
import ttkbootstrap as ttk
import sia_app.utils.dataset_utils as dataset_utils
import sia_app.utils.global_variables as global_vars
import sia_app.utils.basic_form_fields as form_fields
import sia_app.utils.project_manager as prj_mgmt
from datetime import datetime
from sia_app.views.templates.tab_view import TabView
from siaplotlib.chart_building import line_chart
from siaplotlib.chart_building.base_builder import ChartBuilder
from siaplotlib.processing import wrangling as plot_wrangling
from siaplotlib.charts.raw_image import ChartImage

class CurrentsChartView(TabView):
  def __init__(self, master, project_path, worksheet_name):
    super().__init__(master, chart_type='CURRENTS_CHART')
    self.project_path = project_path
    self.worksheet_name = worksheet_name

    self.depth_list = dataset_utils.get_depth_values()
    self.dataset_lon_values = dataset_utils.get_longitude_values()
    self.dataset_lat_values = dataset_utils.get_latitude_values()

    self.__progress_bar = None

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    # ------------------ Elements of the view  ------------------

    title_view_label = ttk.Label(self.col2_user_params_frame, text='Corrientes', font=('TkDefaultFont', 14))
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

    label_text = 'Nivel de agrupación:'
    self.stride_entry = form_fields.create_entry_row(form_entries_frame, label_text)

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
        self.stride_entry.get(),
        self.lon_min_entry.get(), 
        self.lon_max_entry.get(),
        self.lat_min_entry.get(), 
        self.lat_max_entry.get(),
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
    stride,
    lon_min, lon_max,
    lat_min, lat_max
  ):
    print('-----------------------------')
    print(f'depth: "{depth}"')
    print(f'chart_title: "{chart_title}"')
    print(f'target_date: "{target_date}"')
    print(f'stride: "{stride}"')
    print(f'lon_min: "{lon_min}"')
    print(f'lon_max: "{lon_max}"')
    print(f'lat_min: "{lat_min}"')
    print(f'lat_max: "{lat_max}"')

    # Hide column 2 with the chart and buttons.
    self.chart_and_btns_frame.pack_forget()
    # Validations.
    valid_fields = self.__fields_validation(depth, chart_title, target_date, stride,
      lon_min, lon_max, lat_min, lat_max)
    if not valid_fields:
      return
    # Start progress bar.
    self.__start_progress_bar()

    try:
      self.__generate_static_chart(depth, chart_title, target_date, stride, 
        lon_min, lon_max, lat_min, lat_max)
    except Exception as err:
      self.__stop_progress_bar()
      tk.messagebox.showerror(title='Error', message=err)

  def __generate_static_chart(
    self,
    depth,
    chart_title,
    target_date,
    stride,
    lon_min, lon_max,
    lat_min, lat_max
  ):
    print(f'-> Static Arror chart image.')
    dataset = global_vars.current_project_dataset 
    lon_min, lon_max = float(lon_min), float(lon_max)
    lat_min, lat_max = float(lat_min), float(lat_max)

    dim_constraints = {
      self.time_dim: [target_date],
      self.depth_dim: depth,
    }
    subset = plot_wrangling.slice_dice(
      dataset=dataset,
      dim_constraints=dim_constraints
    )
    dim_constraints = {
      self.lon_dim: slice(lon_min, lon_max),
      self.lat_dim: slice(lat_min, lat_max),
    }
    subset = plot_wrangling.slice_dice(
      dataset=subset,
      dim_constraints=dim_constraints,
      squeeze=False
    )
    if len(subset[self.lat_dim]) < 4 or len(subset[self.lon_dim]) < 4:
      message = 'La zona seleccionada, rango de latitud o longitud, es muy pequeña para generar el gráfico. '
      message += 'Por favor, seleccione una zona más grande.'
      raise Exception(message)
      return
    if 'current_velocity' in subset and dataset_utils.is_dataarray_empty(subset['current_velocity']):
      message = 'No hay datos para los parámetros seleccionados. '
      message += 'Por favor, seleccione otros valores.'
      raise Exception(message)
      return

    self.chart_builder = line_chart.StaticArrowChartBuilder(
      dataset=subset,
      eastward_var_name = self.eastward_var,
      northward_var_name = self.northward_var,
      lat_dim_name = self.lat_dim,
      lon_dim_name = self.lon_dim,
      depth_dim_name = self.depth_dim,
      time_dim_name = self.time_dim,
      grouping_level = int(stride),
      title = chart_title,
      var_label='Velocidad [m/s]',
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
    chart_subset_info = dataset_utils.dataarray_info(subset)
    self.show_chart_info(chart_info=chart_subset_info)
    print(f'-> Chart info extracted and displayed.', file=sys.stderr)
    self.__save_chart_parameters_and_img(chart_img_rel_path, chart_subset_info)
    print(f'-> Current state saved. Parameters, chart image and chart info.', file=sys.stderr)

    self.__stop_progress_bar()
    self.chart_and_btns_frame.pack(fill='both', expand=1)

  def __static_failure_build_callback(self, err):
    print('--- An error ocurr while building the chart. ---', file=sys.stderr)
    traceback.print_exception(err, file=sys.stderr)
    # print(err, file=sys.stderr)

    err_msg = 'Ocurrió un error al generar el gráfico.\n'
    err_msg += 'Revisa nuevamente los parámetros de creación del gráfico.'

    self.__stop_progress_bar()
    tk.messagebox.showerror(title='Error', message=err_msg)
    traceback.print_exception(err)

  def __fields_validation(
    self, 
    depth, 
    chart_title,
    target_date,
    stride,
    lon_min, lon_max,
    lat_min, lat_max
  ):
    chart_title = chart_title.strip()
    
    # Empty fields validation.
    empty_fields = []
    if depth == '': empty_fields.append('Profundidad')
    if chart_title == '': empty_fields.append('Título del gráfico')
    if target_date == '': empty_fields.append('Fecha objetivo')
    if stride == '': empty_fields.append('Nivel de agrupación')
    if lon_min == '': empty_fields.append('Longitud mínima')
    if lon_max == '': empty_fields.append('Longitud máxima')
    if lat_min == '': empty_fields.append('Latitud mínima')
    if lat_max == '': empty_fields.append('Latitud máxima')

    if len(empty_fields) > 0:
      message = 'Todos los campos son obligatorios. Datos faltantes: \n'
      message += ', '.join(empty_fields)
      tk.messagebox.showerror(title='Error', message=message)
      return False

    # Validate stride type and limits.
    try:
      stride = int(stride)
      if stride <= 0:
        raise Exception()
    except:
      message = 'Nivel de agrupación debe ser un número entero positivo.'
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

      if lon_max < min_dataset_lon or lon_min > max_dataset_lon or \
        lat_max < min_dataset_lat or lat_min > max_dataset_lat:
        message = 'La longitud o latitud estan fuera de los rangos del dataset.\n'
        message += f'Rango de longitud: {min_dataset_lon}° a {max_dataset_lon}°.\n'
        message += f'Rango de latitud: {min_dataset_lat}° a {max_dataset_lat}°.'
        raise Exception(message)
    except Exception as err:
      tk.messagebox.showerror(title='Error', message=err)
      return False

    return True

  def __start_progress_bar(self):
    self.__progress_bar.start()

  def __stop_progress_bar(self):
    self.__progress_bar.stop()

  def __save_chart_parameters_and_img(self, chart_img_rel_path, chart_subset_info):
    parameters = {
      'depth': self.depth_cb.get(),
      'chart_title': self.chart_title_entry.get(),
      'target_date': self.target_date_entry.entry.get(),
      'stride': self.stride_entry.get(),
      'lon_min': self.lon_min_entry.get(),
      'lon_max': self.lon_max_entry.get(),
      'lat_min': self.lat_min_entry.get(),
      'lat_max': self.lat_max_entry.get()
    }

    prj_mgmt.save_chart_parameters_and_img(
      self.project_path, 
      self.worksheet_name, 
      parameters, 
      chart_img_rel_path,
      chart_subset_info
    )

  def __restore_params_and_img_if_apply(self):
    chart_data = prj_mgmt.get_chart_parameters_and_img(self.project_path, self.worksheet_name)
    parameters = chart_data['parameters']
    chart_img_rel_path = chart_data['chart_img_rel_path']
    chart_subset_info = chart_data['chart_subset_info']

    if len(parameters) > 0:
      self.depth_cb.set(parameters['depth'])
      self.chart_title_entry.insert(0, parameters['chart_title'])
      self.target_date_entry.entry.delete(0, 'end')
      self.target_date_entry.entry.insert(0, parameters['target_date'])
      self.stride_entry.insert(0, parameters['stride'])
      self.lon_min_entry.delete(0, 'end')
      self.lon_min_entry.insert(0, parameters['lon_min'])
      self.lon_max_entry.delete(0, 'end')
      self.lon_max_entry.insert(0, parameters['lon_max'])
      self.lat_min_entry.delete(0, 'end')
      self.lat_min_entry.insert(0, parameters['lat_min'])
      self.lat_max_entry.delete(0, 'end')
      self.lat_max_entry.insert(0, parameters['lat_max'])

      img_path = pathlib.Path(global_vars.current_project_path, chart_img_rel_path)
      # Restore chart builder.
      chart_builder = ChartBuilder(
        dataset=None,
        log_stream=sys.stderr,
        verbose=True)
      chart_image = ChartImage(
        img_source=img_path,
        verbose=chart_builder.verbose,
        log_stream=chart_builder.log_stream)
      chart_builder._chart = chart_image
      self.chart_builder = chart_builder

      self.show_static_chart_img(img_path)

      self.show_chart_info(chart_subset_info)