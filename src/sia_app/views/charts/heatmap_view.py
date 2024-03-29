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
from sia_app.views.templates.tab_view import TabView
from siaplotlib.chart_building import level_chart
from siaplotlib.chart_building.base_builder import ChartBuilder
from siaplotlib.charts.raw_image import ChartImage
from siaplotlib.processing import wrangling as plot_wrangling
from datetime import datetime

class HeatMapView(TabView):
  def __init__(self, master, project_path, worksheet_name):
    super().__init__(master, chart_type='HEATMAP')
    self.project_path = project_path
    self.worksheet_name = worksheet_name

    self.__build_method = None
    self.__static_build_method_frame = None
    self.__animated_build_method_frame = None

    self.variables_long_names = dataset_utils.get_variables_long_names()
    self.variables_units = dataset_utils.get_variables_units()
    self.depth_list = dataset_utils.get_depth_values()
    self.dataset_lon_values = dataset_utils.get_longitude_values()
    self.dataset_lat_values = dataset_utils.get_latitude_values()
    self.dataset_date_values = dataset_utils.get_time_values()
    self.duration_unit_dict = {
      'Frames por segundo': 'FRAMES_PER_SECOND',
      'Segundos por frame': 'SECONDS_PER_FRAME'
    }
    self.duration_unit = None
    self.duration = None

    self.__progress_bar = None

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    # ------------------ Elements of the view  ------------------

    title_view_label = ttk.Label(self.col2_user_params_frame, text='Heatmap', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=10)

    # Form.
    form_frame = ttk.Frame(self.col2_user_params_frame, bootstyle='default')
    form_frame.pack(fill='x', padx=20, pady=10)

    form_entries_frame = ttk.Frame(form_frame)
    form_entries_frame.pack(fill='x')

    label_text = 'Método de construcción:'
    build_method_list = ['Estático', 'Animado']
    self.build_method_cb = form_fields.create_combobox_row(form_entries_frame, label_text, build_method_list)
    self.build_method_cb.bind("<<ComboboxSelected>>", self.__selected_build_method_handler)

    label_text = 'Variable:'
    options = list(self.variables_long_names.keys())
    self.variable_cb = form_fields.create_combobox_row(form_entries_frame, label_text, options)

    label_text = 'Profundidad [m]:'
    options = [''] + self.depth_list
    self.depth_cb = form_fields.create_combobox_row(form_entries_frame, label_text, options)

    label_text = 'Título del gráfico:'
    self.chart_title_entry = form_fields.create_entry_row(form_entries_frame, label_text)

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

    # Following entries will be hidden or shown depending on the selected build method.

    self.__static_build_method_frame = ttk.Frame(form_entries_frame)
    self.__static_build_method_frame.pack_forget()
    label_text = 'Fecha objetivo:'
    self.target_date_entry = form_fields.create_date_entry_row(self.__static_build_method_frame, label_text)

    self.__animated_build_method_frame = ttk.Frame(form_entries_frame)
    self.__animated_build_method_frame.pack_forget()

    label_text = 'Unidad de duración:'
    duration_unit_list = list(self.duration_unit_dict.keys())
    self.duration_cb = form_fields.create_combobox_row(self.__animated_build_method_frame, label_text, duration_unit_list)

    label_text = 'Duración'
    self.duration_entry = form_fields.create_entry_row(self.__animated_build_method_frame, label_text)

    min_dataset_date = min(self.dataset_date_values).date()
    label_text = 'Fecha de inicio:'
    self.start_date_entry = form_fields.create_date_entry_row(self.__animated_build_method_frame, label_text)
    self.start_date_entry.entry.delete(0, 'end')
    self.start_date_entry.entry.insert(0, min_dataset_date)

    max_dataset_date = max(self.dataset_date_values).date()
    label_text = 'Fecha de fin:'
    self.end_date_entry = form_fields.create_date_entry_row(self.__animated_build_method_frame, label_text)
    self.end_date_entry.entry.delete(0, 'end')
    self.end_date_entry.entry.insert(0, max_dataset_date)

    # Restore previous values from the project file if was configured.
    self.__restore_params_and_img_if_apply()

    # Apply button.
    connect_button = ttk.Button(
      form_frame, 
      text='Generar gráfico', 
      command=lambda: self.__start_creation_chart(
        self.build_method_cb.get(),
        self.variable_cb.get(), 
        self.depth_cb.get(),
        self.chart_title_entry.get(), 
        self.palette_colors_cb.get(),
        self.lon_min_entry.get(),
        self.lon_max_entry.get(),
        self.lat_min_entry.get(),
        self.lat_max_entry.get(),
        target_date=self.target_date_entry.entry.get(), # Only for static build method.
        duration_unit=self.duration_cb.get(), 
        duration=self.duration_entry.get(), # Only for animated build method.
        start_date=self.start_date_entry.entry.get(), 
        end_date=self.end_date_entry.entry.get() # Only for animated build method.
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
    build_method,
    variable,
    depth,
    chart_title,
    palette_colors,
    lon_min,
    lon_max,
    lat_min,
    lat_max,
    target_date=None,
    duration_unit=None,
    duration=None,
    start_date=None,
    end_date=None
  ):
    print('-----------------------------', file=sys.stderr)
    print(f'build_method: "{build_method}"', file=sys.stderr)
    print(f'variable: "{variable}"', file=sys.stderr)
    print(f'depth: "{depth}"', file=sys.stderr)
    print(f'chart_title: "{chart_title}"', file=sys.stderr)
    print(f'palette_colors: "{palette_colors}"', file=sys.stderr)
    print(f'lon_min: "{lon_min}"', file=sys.stderr)
    print(f'lon_max: "{lon_max}"', file=sys.stderr)
    print(f'lat_min: "{lat_min}"', file=sys.stderr)
    print(f'lat_max: "{lat_max}"', file=sys.stderr)
    print(f'target_date: "{target_date}"', file=sys.stderr)
    print(f'duration_unit: "{duration_unit}"', file=sys.stderr)
    print(f'duration: "{duration}"', file=sys.stderr)
    print(f'start_date: "{start_date}"', file=sys.stderr)
    print(f'end_date: "{end_date}"', file=sys.stderr)

    # Hide column 2 with the chart and buttons.
    self.chart_and_btns_frame.pack_forget()
    # Validations.
    valid_fields = self.__fields_validation(
      build_method, 
      variable, 
      depth, 
      chart_title, 
      palette_colors, 
      lon_min,
      lon_max,
      lat_min,
      lat_max,
      target_date, 
      duration_unit, 
      duration, 
      start_date, 
      end_date
    )
    if not valid_fields:
      return
    # Start progress bar.
    self.__start_progress_bar()

    try:
      if self.__build_method == 'static':
        self.__generate_static_chart(variable, depth, chart_title, palette_colors,
          lon_min, lon_max, lat_min, lat_max, target_date)
      elif self.__build_method == 'animated':
        self.__generate_animated_chart(variable, depth, chart_title, palette_colors,
          lon_min, lon_max, lat_min, lat_max, duration_unit, duration, start_date, end_date)
    except Exception as err:
      self.__stop_progress_bar()
      tk.messagebox.showerror(title='Error', message=err)

  def __generate_static_chart(
    self,
    variable,
    depth,
    chart_title,
    palette_colors,
    lon_min,
    lon_max,
    lat_min,
    lat_max,
    target_date
  ):
    print(f'-> Heatmap static image for "{variable}" variable.', file=sys.stderr)
    dataset = global_vars.current_project_dataset
    var_name = self.variables_long_names[variable]
    lon_min, lon_max = float(lon_min), float(lon_max)
    lat_min, lat_max = float(lat_min), float(lat_max)

    dim_constraints = { self.time_dim: [target_date] }
    if depth != '':
      dim_constraints[self.depth_dim] = [depth]
    subset = plot_wrangling.slice_dice(
      dataset=dataset,
      dim_constraints=dim_constraints,
      var=var_name
    )
    dim_constraints = {
      self.lon_dim: slice(lon_min, lon_max),
      self.lat_dim: slice(lat_min, lat_max)
    }
    subset = plot_wrangling.slice_dice(
      dataset=subset,
      dim_constraints=dim_constraints,
      squeeze=False
    )
    if len(subset[self.lat_dim]) < 2 or len(subset[self.lon_dim]) < 2:
      message = 'La zona seleccionada, rango de latitud o longitud, es muy pequeña para generar el gráfico. '
      message += 'Por favor, seleccione una zona más grande.'
      raise Exception(message)
      return
    if dataset_utils.is_dataarray_empty(subset):
      message = 'No hay datos para los parámetros seleccionados. '
      message += 'Por favor, seleccione otros valores.'
      raise Exception(message)
      return

    self.chart_builder = level_chart.StaticHeatMapBuilder(
      dataset=subset,
      title=chart_title.strip(),
      var_label=f'{variable} [{self.variables_units[var_name]}]',
      lat_dim_name=self.lat_dim,
      lon_dim_name=self.lon_dim,
      color_palette=palette_colors
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
    self.play_chart_btn.pack_forget() # Hide button to play gif (only for animations).

  def __static_failure_build_callback(self, err):
    print('--- An error ocurr while building the chart. ---', file=sys.stderr)
    traceback.print_exception(err, file=sys.stderr)
    # print(err, file=sys.stderr)

    err_msg = 'Ocurrió un error al generar el gráfico.\n'
    if 'is not a valid dimension or coordinate' in str(err):
      dimension_pattern = r"'(.*?)'" # The dimension is wrapped in single quotes.
      dimension_err = re.findall(dimension_pattern, str(err))
      err_msg += f'Para la variable en uso, la dimensión {dimension_err[0]} no es válida.'
    else:
      err_msg += 'Revisa nuevamente los parámetros de creación del gráfico.'

    self.__stop_progress_bar()
    tk.messagebox.showerror(title='Error', message=err_msg)
    traceback.print_exception(err)

  def __generate_animated_chart(
    self,
    variable,
    depth,
    chart_title,
    palette_colors,
    lon_min,
    lon_max,
    lat_min,
    lat_max,
    duration_unit,
    duration,
    start_date,
    end_date
  ):
    print(f'-> Heatmap gif for "{variable}" variable.', file=sys.stderr)
    dataset = global_vars.current_project_dataset
    var_name = self.variables_long_names[variable]
    lon_min, lon_max = float(lon_min), float(lon_max)
    lat_min, lat_max = float(lat_min), float(lat_max)

    dim_constraints = { self.time_dim: slice(start_date, end_date) }
    if depth != '':
      dim_constraints[self.depth_dim] = [depth]
    subset = plot_wrangling.slice_dice(
      dataset=dataset,
      dim_constraints=dim_constraints,
      var=var_name
    )
    dim_constraints = {
      self.lon_dim: slice(lon_min, lon_max),
      self.lat_dim: slice(lat_min, lat_max)
    }
    subset = plot_wrangling.slice_dice(
      dataset=subset,
      dim_constraints=dim_constraints,
      squeeze=False
    )
    if len(subset[self.lat_dim]) < 2 or len(subset[self.lon_dim]) < 2:
      message = 'La zona seleccionada, rango de latitud o longitud, es muy pequeña para generar el gráfico. '
      message += 'Por favor, seleccione una zona más grande.'
      raise Exception(message)
      return
    if dataset_utils.is_dataarray_empty(subset):
      message = 'No hay datos para los parámetros seleccionados. '
      message += 'Por favor, seleccione otros valores.'
      raise Exception(message)
      return

    self.duration_unit = self.duration_unit_dict[duration_unit]
    self.duration = int(duration) if self.duration_unit == 'FRAMES_PER_SECOND' else round(float(duration), 2)

    self.chart_builder = level_chart.AnimatedHeatMapBuilder(
      dataset=subset,
      title=chart_title.strip(),
      var_label=f'{variable} [{self.variables_units[var_name]}]',
      time_dim_name=self.time_dim,
      lat_dim_name=self.lat_dim,
      lon_dim_name=self.lon_dim,
      duration=self.duration,
      duration_unit=self.duration_unit,
      color_palette=palette_colors
    )
    self.chart_builder.build(
      success_callback=self.__animated_success_build_callback, 
      failure_callback=self.__animated_failure_build_callback
    )

  def __animated_success_build_callback(self, chart_builder, subset):
    print(f'-> Image built.', file=sys.stderr)
    gif_buffer = chart_builder._chart.get_buffer()
    self.show_animated_chart_img(gif_buffer, self.duration_unit, self.duration)

    chart_img_rel_path = self.save_current_img_chart(self.worksheet_name, '.gif')
    print(f'-> Animated chart image saved in "{chart_img_rel_path}"', file=sys.stderr)
    chart_subset_info = dataset_utils.dataarray_info(subset)
    self.show_chart_info(chart_info=chart_subset_info)
    print(f'-> Chart info extracted and displayed.', file=sys.stderr)
    self.__save_chart_parameters_and_img(chart_img_rel_path, chart_subset_info)
    print(f'-> Current state saved. Parameters, chart image and chart info.', file=sys.stderr)

    self.__stop_progress_bar()
    self.chart_and_btns_frame.pack(fill='both', expand=1)
    self.play_chart_btn.pack() # Show button to play gif.

  def __animated_failure_build_callback(self, err):
    print('--- An error ocurr while building the chart. ---', file=sys.stderr)
    traceback.print_exception(err, file=sys.stderr)
    # print(err, file=sys.stderr)
    
    err_msg = 'Ocurrió un error al generar el gráfico.\n'
    if 'is not a valid dimension or coordinate' in str(err):
      dimension_pattern = r"'(.*?)'" # The dimension is wrapped in single quotes.
      dimension_err = re.findall(dimension_pattern, str(err))
      err_msg += f'Para la variable en uso, la dimensión {dimension_err[0]} no es válida.'
    elif 'numpy.nanmin raises on a.size==0 and axis=None' in str(err):
      err_msg += 'Rango de fechas no disponible, por favor consulte la información '
      err_msg += 'del dataset respecto a la dimensión de tiempo y su resolución temporal '
      err_msg += 'en la pestaña de "Información de datos"'
    else:
      err_msg += 'Revisa nuevamente los parámetros de creación del gráfico.'

    self.__stop_progress_bar()
    tk.messagebox.showerror(title='Error', message=err_msg)
    traceback.print_exception(err)

  def __fields_validation(
    self, 
    build_method, 
    variable, 
    depth, 
    chart_title, 
    palette_colors,
    lon_min,
    lon_max,
    lat_min,
    lat_max,
    target_date=None,
    duration_unit=None,
    duration=None,
    start_date=None,
    end_date=None
  ):
    chart_title = chart_title.strip()
    
    # Empty fields validation.
    empty_fields = []
    if build_method == '': empty_fields.append('Método de construcción')
    if variable == '': empty_fields.append('Variable')
    # if depth == '': empty_fields.append('Profundidad')
    if chart_title == '': empty_fields.append('Título del gráfico')
    if palette_colors == '': empty_fields.append('Paleta de colores')
    if lon_min == '': empty_fields.append('Longitud mínima')
    if lon_max == '': empty_fields.append('Longitud máxima')
    if lat_min == '': empty_fields.append('Latitud mínima')
    if lat_max == '': empty_fields.append('Latitud máxima')
    if self.__build_method == 'static':
      if target_date == '' or target_date == None:
        empty_fields.append('Fecha de objetivo')
    elif self.__build_method == 'animated':
      if duration_unit == '' or duration_unit == None:
        empty_fields.append('Unidad de duración')
      duration = duration.strip()
      if duration == '' or duration == None:
        empty_fields.append('Duración')
      if start_date == '' or start_date == None:
        empty_fields.append('Fecha inicial')
      if end_date == '' or end_date == None:
        empty_fields.append('Fecha final')

    if len(empty_fields) > 0:
      message = 'Todos los campos son obligatorios. Datos faltantes: \n'
      message += ', '.join(empty_fields)
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

    if self.__build_method == 'static':
      # Validate target date format.
      try:
        target_date = datetime.strptime(target_date, '%Y-%m-%d')
      except:
        message = 'La fecha objetivo debe tener el formato "YYYY-MM-DD".'
        tk.messagebox.showerror(title='Error', message=message)
        return False
    elif self.__build_method == 'animated':
      # Validate duration value limits.
      if self.duration_unit_dict[duration_unit] == 'FRAMES_PER_SECOND':
        try:
          duration = int(duration)
          if duration <= 0:
            raise Exception
        except:
          message = 'La duración debe ser un número entero positivo, '
          message += f'cuando la unidad de duración es "{duration_unit}".'
          tk.messagebox.showerror(title='Error', message=message)
          return False
      elif self.duration_unit_dict[duration_unit] == 'SECONDS_PER_FRAME':
        try:
          duration = round(float(duration), 2)
          if duration <= 0 or duration > 10:
            raise Exception
        except:
          message = 'La duración debe ser un número flotante mayor a 0 y menor o igual a 10, '
          message += f'cuando la unidad de duración es "{duration_unit}".'
          tk.messagebox.showerror(title='Error', message=message)
          return False

      # Validate start and end dates format.
      try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
      except:
        message = 'Las fechas deben tener el formato "YYYY-MM-DD".'
        tk.messagebox.showerror(title='Error', message=message)
        return False

      # Validate start and end dates order.
      if start_date >= end_date:
        message = 'La fecha inicial debe ser menor a la fecha final.'
        tk.messagebox.showerror(title='Error', message=message)
        return False

      # Validate start and end dates range.
      min_dataset_date = min(self.dataset_date_values).date()
      max_dataset_date = max(self.dataset_date_values).date()
      if end_date < min_dataset_date or start_date > max_dataset_date:
        message = 'Las fechas deben estar dentro del rango de fechas del dataset. '
        message += f'El rango de fechas del dataset va del {min_dataset_date} hasta el {max_dataset_date}.'
        tk.messagebox.showerror(title='Error', message=message)
        return False

    return True

  def __selected_build_method_handler(self, event):
    build_method_selected = event.widget.get()
    if build_method_selected == 'Estático':
      self.__build_method = 'static'
      self.__static_build_method_frame.pack(fill='x')
      self.__animated_build_method_frame.pack_forget()
    else:
      self.__build_method = 'animated'
      self.__animated_build_method_frame.pack(fill='x')
      self.__static_build_method_frame.pack_forget()

  def __start_progress_bar(self):
    self.__progress_bar.start()

  def __stop_progress_bar(self):
    self.__progress_bar.stop()

  def __save_chart_parameters_and_img(self, chart_img_rel_path, chart_subset_info):
    parameters = {
      'build_method': self.build_method_cb.get(),
      'variable': self.variable_cb.get(),
      'depth': self.depth_cb.get(),
      'chart_title': self.chart_title_entry.get(),
      'palette_colors': self.palette_colors_cb.get(),
      'lon_min': self.lon_min_entry.get(),
      'lon_max': self.lon_max_entry.get(),
      'lat_min': self.lat_min_entry.get(),
      'lat_max': self.lat_max_entry.get(),
      'target_date': self.target_date_entry.entry.get(),
      'duration_unit': self.duration_cb.get(),
      'duration': self.duration_entry.get(),
      'start_date': self.start_date_entry.entry.get(),
      'end_date': self.end_date_entry.entry.get()
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
      self.build_method_cb.set(parameters['build_method'])
      self.variable_cb.set(parameters['variable'])
      self.depth_cb.set(parameters['depth'])
      self.chart_title_entry.insert(0, parameters['chart_title'])
      self.palette_colors_cb.set(parameters['palette_colors'])
      self.lon_min_entry.delete(0, 'end')
      self.lon_min_entry.insert(0, parameters['lon_min'])
      self.lon_max_entry.delete(0, 'end')
      self.lon_max_entry.insert(0, parameters['lon_max'])
      self.lat_min_entry.delete(0, 'end')
      self.lat_min_entry.insert(0, parameters['lat_min'])
      self.lat_max_entry.delete(0, 'end')
      self.lat_max_entry.insert(0, parameters['lat_max'])
      self.target_date_entry.entry.delete(0, 'end')
      self.target_date_entry.entry.insert(0, parameters['target_date'])
      self.duration_cb.set(parameters['duration_unit'])
      self.duration_entry.insert(0, parameters['duration'])
      self.start_date_entry.entry.delete(0, 'end')
      self.start_date_entry.entry.insert(0, parameters['start_date'])
      self.end_date_entry.entry.delete(0, 'end')
      self.end_date_entry.entry.insert(0, parameters['end_date'])

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

      if parameters['build_method'] == 'Estático':
        self.__build_method = 'static'
        self.__static_build_method_frame.pack(fill='x')

        self.show_static_chart_img(img_path)
      else:
        self.__build_method = 'animated'
        self.__animated_build_method_frame.pack(fill='x')

        self.show_animated_chart_img(
          img_path, 
          self.duration_unit_dict[parameters['duration_unit']], 
          int(parameters['duration'])
        )
        self.play_chart_btn.pack() # Show button to play gif.

      self.show_chart_info(chart_subset_info)