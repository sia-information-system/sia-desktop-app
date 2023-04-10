import pathlib
import re
import sys
import tkinter as tk
import ttkbootstrap as ttk
import utils.dataset_utils as dataset_utils
import utils.global_variables as global_vars
import utils.basic_form_fields as form_fields
from views.templates.tab_view import TabView
from siaplotlib.chart_building import line_chart
from PIL import ImageTk, Image
from datetime import datetime

class SinglePointTimeSeriesView(TabView):
  def __init__(self, master):
    super().__init__(master, chart_type='TIME_SERIES')
    self.variables_long_names = dataset_utils.get_variables_long_names()
    self.variables_units = dataset_utils.get_variables_units()
    self.depth_list = dataset_utils.get_depth_values()

    self.__progress_bar = None

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    # ------------------ Elements of the view  ------------------

    title_view_label = ttk.Label(self.col2_user_params_frame, text='Series de Tiempo', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=10)

    # Form.
    form_frame = ttk.Frame(self.col2_user_params_frame, bootstyle='default')
    form_frame.pack(fill='x', padx=20, pady=10)

    form_entries_frame = ttk.Frame(form_frame)
    form_entries_frame.pack(fill='x')

    label_text = 'Variable:'
    options = list(self.variables_long_names.keys())
    variable_cb = form_fields.create_combobox_row(form_entries_frame, label_text, options)

    label_text = 'Profundidad(es) [m]:'
    depth_cb_list = form_fields.MultipleCombobox(
      form_entries_frame, 
      label_text, 
      self.depth_list, 
      readonly=False
    )

    label_text = 'Título del gráfico:'
    chart_title_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Longitud:'
    longitude_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Latitud: '
    latitude_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Fecha de inicio:'
    start_date_entry = form_fields.create_date_entry_row(form_entries_frame, label_text)
    label_text = 'Fecha de fin:'
    end_date_entry = form_fields.create_date_entry_row(form_entries_frame, label_text)


    # Apply button.
    connect_button = ttk.Button(
      form_frame, 
      text='Generar gráfico', 
      command=lambda: self.__start_creation_chart(
        variable_cb.get(), depth_cb_list.get(),
        chart_title_entry.get(), longitude_entry.get(), latitude_entry.get(),
        start_date=start_date_entry.entry.get(), end_date=end_date_entry.entry.get() 
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
    variable,
    depths,
    chart_title,
    longitude,
    latitude,
    start_date,
    end_date
  ):
    print('-----------------------------', file=sys.stderr)
    print(f'variable: "{variable}"', file=sys.stderr)
    print(f'depths: "{depths}"', file=sys.stderr)
    print(f'chart_title: "{chart_title}"', file=sys.stderr)
    print(f'longitude: "{longitude}"', file=sys.stderr)
    print(f'latitude: "{latitude}"', file=sys.stderr)
    print(f'start_date: "{start_date}"', file=sys.stderr)
    print(f'end_date: "{end_date}"', file=sys.stderr)

    # Hide column 2 with the chart and buttons.
    self.chart_and_btns_frame.pack_forget()
    # Validations.
    dims_and_var_configured = self.dataset_dims_and_vars_validation()
    if not dims_and_var_configured:
      return
    valid_fields = self.__fields_validation(variable, depths, chart_title, longitude, latitude, 
      start_date, end_date)
    if not valid_fields:
      return
    # Start progress bar.
    self.__start_progress_bar()

    try:
      self.__generate_static_chart(variable, depths, chart_title, longitude, latitude, 
        start_date, end_date)
    except Exception as err:
      self.__stop_progress_bar()
      tk.messagebox.showerror(title='Error', message=err)

  def __generate_static_chart(
    self,
    variable,
    depths,
    chart_title,
    longitude,
    latitude,
    start_date,
    end_date
  ):
    print(f'-> Static Time series image for "{variable}" variable.', file=sys.stderr)
    dataset = global_vars.current_project_dataset
    variable = self.variables_long_names[variable]
    date_range = slice(start_date, end_date)
    grouping_dim_name = None
    depths = [float(depth) for depth in depths]

    dim_constraints = {
      self.time_dim: date_range,
      self.lat_dim: latitude,
      self.lon_dim: longitude
    }
    if len(depths) > 0:
      dim_constraints[self.depth_dim] = depths
      grouping_dim_name = self.depth_dim

    self.chart_builder = line_chart.SinglePointTimeSeriesBuilder(
      dataset=dataset,
      var_name=variable,
      title=chart_title.strip(),
      var_label=self.variables_units[variable],
      dim_constraints=dim_constraints,
      lat_dim_name=self.lat_dim,
      lon_dim_name=self.lon_dim,
      grouping_dim_label='Depth (m)',
      grouping_dim_name=grouping_dim_name,
      time_dim_label='Dates',
      time_dim_name=self.time_dim,
    )
    self.chart_builder.build(
      success_callback=self.__static_success_build_callback, 
      failure_callback=self.__static_failure_build_callback
    )

  def __static_success_build_callback(self, chart_builder):
    print(f'-> Image built.', file=sys.stderr)
    img_buffer = chart_builder._chart.get_buffer()
    self.chart_img = ImageTk.PhotoImage(Image.open(img_buffer))
    self.chart_img_label.configure(image=self.chart_img)

    self.__stop_progress_bar()
    self.chart_and_btns_frame.pack(fill='both', expand=1)

  def __static_failure_build_callback(self, err):
    print('--- An error ocurr while building the chart. ---', file=sys.stderr)
    print(err, file=sys.stderr)

    err_msg = 'Ocurrió un error al generar el gráfico.\n'
    if 'is not a valid dimension or coordinate' in str(err):
      dimension_pattern = r"'(.*?)'" # The dimension is wrapped in single quotes.
      dimension_err = re.findall(dimension_pattern, str(err))
      err_msg += f'Para la variable en uso, la dimensión {dimension_err[0]} no es válida.'
    else:
      err_msg += 'Revisa nuevamente los parámetros de creación del gráfico.'

    self.__stop_progress_bar()
    tk.messagebox.showerror(title='Error', message=err_msg)

  def __fields_validation(
    self, 
    variable, 
    depths, 
    chart_title,
    longitude,
    latitude,
    start_date=None,
    end_date=None
  ):
    chart_title = chart_title.strip()
    
    # Empty fields validation.
    empty_fields = []
    if variable == '': empty_fields.append('Variable')
    # if len(depths) == 0: empty_fields.append('Profundidad(es)')
    if chart_title == '': empty_fields.append('Título del gráfico')
    if longitude == '': empty_fields.append('Longitud')
    if latitude == '': empty_fields.append('Latitud')
    if start_date == '': empty_fields.append('Fecha inicial')
    if end_date == '': empty_fields.append('Fecha final')

    if len(empty_fields) > 0:
      message = 'Todos los campos son obligatorios. Datos faltantes: \n'
      message += ', '.join(empty_fields)
      tk.messagebox.showerror(title='Error', message=message)
      return False

    # Validate depths
    try:
      if len(depths) != len(set(depths)):
        raise Exception('Profundidades duplicadas. Asegúrese de que no haya profundidades repetidas.')

      for depth in depths:
        if depth == '':
          message = 'Profundidad(es) sin valor, asegúrese de que cada profundidad tenga un valor.'
          message += ' Si no desea especificar una profundidad, elimínela.'
          raise Exception(message)
          break
    except Exception as e:
      tk.messagebox.showerror(title='Error', message=e)
      return False

    # Validate longitude and latitude type and range.
    try:
      point_lon = float(longitude)
      point_lat = float(latitude)

      dataset_lon_values = dataset_utils.get_longitude_values()
      min_dataset_lon, max_dataset_lon = min(dataset_lon_values), max(dataset_lon_values)
      dataset_lat_values = dataset_utils.get_latitude_values()
      min_dataset_lat, max_dataset_lat = min(dataset_lat_values), max(dataset_lat_values)
      if point_lon < min_dataset_lon or point_lon > max_dataset_lon or \
        point_lat < min_dataset_lat or point_lat > max_dataset_lat:
        message = 'La longitud y la latitud deben estar dentro del rango del dataset.\n'
        message += f'Rango de longitud: {min_dataset_lon}° a {max_dataset_lon}°.\n'
        message += f'Rango de latitud: {min_dataset_lat}° a {max_dataset_lat}°.'
        tk.messagebox.showerror(title='Error', message=message)
        return False
    except:
      message = 'La longitud y la latitud deben ser números flotantes.'
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
    dataset_date_values = dataset_utils.get_time_values()
    min_dataset_date = dataset_date_values[0].date()
    max_dataset_date = dataset_date_values[-1].date()
    if end_date < min_dataset_date or start_date > max_dataset_date:
      message = 'Las fechas deben estar dentro del rango de fechas del dataset. '
      message += f'El rango de fechas del dataset va del {min_dataset_date} hasta el {max_dataset_date}.'
      tk.messagebox.showerror(title='Error', message=message)
      return False

    return True

  def __start_progress_bar(self):
    self.__progress_bar.start()

  def __stop_progress_bar(self):
    self.__progress_bar.stop()
