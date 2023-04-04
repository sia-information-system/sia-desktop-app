import pathlib
import tkinter as tk
import ttkbootstrap as ttk
import utils.dataset_utils as dataset_utils
import utils.global_variables as global_vars
import utils.basic_form_fields as form_fields
from views.templates.tab_view import TabView
from omdepplotlib.chart_building import line_chart
from PIL import ImageTk, Image
from datetime import datetime

class SinglePointTimeSeriesView(TabView):
  def __init__(self, master):
    super().__init__(master, chart_type='TIME_SERIES')
    self.variable_list = dataset_utils.get_variables()
    self.depth_list = dataset_utils.get_depth_values()

    self.__progress_bar = None
    # TODO: Revisar de donde sacar lo de los labels.
    self.plot_measure_label = {
      'thetao': 'Temperature (C°)',
      'vo': 'Northward velocity (m/s)',
      'uo': 'Eastward velocity (m/s)',
      'so': 'Salinity (PSU)',
      'zos': 'Sea surface height (m)'
    }

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
    variable_cb = form_fields.create_combobox_row(form_entries_frame, label_text, self.variable_list)

    label_text = 'Profundidad(es) [m]:'
    default_depth = self.depth_list[0]
    depth1_cb = form_fields.create_combobox_row(form_entries_frame, label_text, self.depth_list, default_option=default_depth)
    depth2_cb = form_fields.create_combobox_row(form_entries_frame, ' ', self.depth_list, readonly=False)
    depth3_cb = form_fields.create_combobox_row(form_entries_frame, ' ', self.depth_list, readonly=False)
    depth4_cb = form_fields.create_combobox_row(form_entries_frame, ' ', self.depth_list, readonly=False)
    depth5_cb = form_fields.create_combobox_row(form_entries_frame, ' ', self.depth_list, readonly=False)

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
        variable_cb.get(),
        [depth1_cb.get(), depth2_cb.get(), depth3_cb.get(), depth4_cb.get(), depth5_cb.get()],
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
      value=20,
      bootstyle='success striped'
    )
    self.__show_and_run_progress_bar()

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
    print('-----------------------------')
    print(f'variable: "{variable}"')
    print(f'depths: "{depths}"')
    print(f'chart_title: "{chart_title}"')
    print(f'longitude: "{longitude}"')
    print(f'latitude: "{latitude}"')
    print(f'start_date: "{start_date}"')
    print(f'end_date: "{end_date}"')

    self.__show_and_run_progress_bar()
    self.chart_and_btns_frame.pack_forget()

    valid_fields = self.__fields_validation(variable, [0,1,2], chart_title, longitude, latitude, 
      start_date, end_date)
    if not valid_fields:
      return

    try:
      dataset = global_vars.current_project_dataset
      self.chart_builder = line_chart.SinglePointTimeSeriesBuilder(dataset=dataset)

      self.__generate_static_chart(variable, depths, chart_title, longitude, latitude, 
        start_date, end_date)

      self.__stop_and_hide_progress_bar()
      self.chart_and_btns_frame.pack(fill='both', expand=1)
    except Exception as e:
      print(f'Error: {e}')
      pass

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
    date_range = slice(start_date, end_date)
    grouping_dim_name = 'depth'
    depths = [int(depth) for depth in depths if depth.isdigit()]
    dim_constraints = {
      'time': date_range,
      'depth': depths,
      'latitude': latitude,
      'longitude': longitude
    }
    if variable == 'zos':
      dim_constraints = {
        'time': date_range,
        'latitude': latitude,
        'longitude': longitude
      }
      grouping_dim_name=None
    print(f'-> Static Time series image for "{variable}" variable.')
    self.chart_builder.build_static(
      var_name=variable,
      title=chart_title.strip(),
      var_label=self.plot_measure_label[variable],
      dim_constraints=dim_constraints,
      lat_dim_name='latitude', # TODO: Solicitar al usuario.
      lon_dim_name='longitude', # TODO: Solicitar al usuario.
      grouping_dim_label='Depth (m)',
      grouping_dim_name=grouping_dim_name, # TODO: Solicitar al usuario.
      time_dim_label='Dates',
      time_dim_name='time', # TODO: Solicitar al usuario.
    )

    img_buffer = self.chart_builder._chart.get_buffer()
    self.chart_img = ImageTk.PhotoImage(Image.open(img_buffer))
    self.chart_img_label.configure(image=self.chart_img)
    # Hide button to play gif.
    self.play_chart_btn.pack_forget()

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

  def __show_and_run_progress_bar(self):
    # print('se llamo a show progress bar')
    self.__progress_bar.pack(pady=10)
    self.__progress_bar.start()

  def __stop_and_hide_progress_bar(self):
    pass
    # print('se llamo a stop and hide progress bar')
    # self.__progress_bar.stop()
    # self.__progress_bar.pack_forget()
