# NOTE: Temporary view. Reused dowload_data_view.py. This was updated in mockups.
import tkinter as tk
import numpy as np
import sys
import ttkbootstrap as ttk
import traceback
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap import constants as ttk_const
from pathlib import Path
from datetime import datetime
from PIL import ImageTk, Image
from utils.global_constants import HOME_DATASETS_DIR, ASSETS_DIR
import utils.basic_form_fields as form_fields
from views.templates.scrollable_view import ScrollableView
from siaextractlib.utils.log import LogStream
from siaextractlib.utils.auth import SimpleAuth
from siaextractlib.utils.metadata import SizeUnit
from siaextractlib.extractors import OpendapExtractor, CopernicusOpendapExtractor
from siaextractlib.processing import wrangling as ext_wrangling
from siaextractlib.utils.metadata import ExtractionDetails
from siaplotlib.chart_building.line_chart import StaticRegionMapBuilder
from siaplotlib.chart_building.base_builder import ChartBuilder


class DimParam:
  def __init__(self, dim_name: str, dim_label:str, input_min, input_max, expected_type, expected_type_label, mapper = None) -> None:
    self.dim_name = dim_name
    self.dim_label = dim_label
    self.input_min = input_min
    self.input_max = input_max
    self.expected_type = expected_type # parse the type with this that should be a function for primitive type.
    self.expected_type_label = expected_type_label
    self.mapper = mapper
  

  def __get_val(self, entry, parse = True):
    val = entry.get().strip()
    if val == '':
      return None
    if not parse:
      return val
    try:
      if self.mapper:
        return self.mapper[val]
    except KeyError:
      print(f'The value {val} is not a key in the existing mapper. Trying to parse the value into {self.expected_type}.', file=sys.stderr)
    try:
      return self.expected_type( val )
    except ValueError:
      raise ValueError(f'"{self.dim_label}" must be of type {self.expected_type}')


  def get_min_val(self, parse=True):
    return self.__get_val(self.input_min, parse=parse)


  def get_max_val(self, parse=True):
    return self.__get_val(self.input_max, parse=parse)


class VarParam:
  def __init__(self, var_name: str, input: tk.BooleanVar) -> None:
    self.var_name = var_name
    self.input = input


class DataExtractorView(ScrollableView):
  def __init__(self, master, root_app_window):
    super().__init__(master)
    self.root_window = root_app_window # Main window. Used to change views.
    self.__progress_bar = None
    self.data_sources = ['Copernicus', 'Otros - OPeNDAP']
    self.terms_status_var = tk.BooleanVar()
    self.map_img = None
    self.extractor: OpendapExtractor = None
    self.connect_button: ttk.Button = None
    self.extract_button: ttk.Button = None
    self.form_frame: ttk.Frame = None
    self.dinamic_form_fields_frame: ttk.Frame = None
    self.dataset_name_entry: ttk.Entry = None
    self.dim_params: list[DimParam] = []
    self.var_params: list[VarParam] = []
    self.lat_min_entry = None
    self.lat_max_entry = None
    self.lon_min_entry = None
    self.lon_max_entry = None
    self.column_2_frame: ttk.Frame = None
    self.map_frame: ttk.Frame = None
    self.map_wrapper_frame: ttk.Frame = None
    self.draw_map_button: ttk.Button = None
    self.dataset_size_label: ttk.Label = None
    self.logging_console_frame: ttk.Frame = None
    self.logging_console = None
    self.log_stream = LogStream(self.__extraction_log_handler)


  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    title_view_label = ttk.Label(self.scroll_frame, text='Descarga de datos', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=10)

    title_view_label = ttk.Label(self.scroll_frame, text='ADVERTENCIA: Mantenga abierta esta ventana mientras se ejecuta su descarga.', font=('TkDefaultFont', 10, 'bold'))
    title_view_label.pack(pady=10)

    self.__progress_bar = ttk.Progressbar(
      self.scroll_frame,
      maximum=40,
      mode='determinate',
      length=100,
      value=0,
      bootstyle='success striped'
    )
    self.__progress_bar.pack(pady=10)

    columns_frame = ttk.Frame(self.scroll_frame)
    columns_frame.pack()

    # Column 1

    form_frame = ttk.Frame(columns_frame)
    form_frame.grid(row=0, column=0, padx=20, pady=10, sticky='nsew')

    title_form_label = ttk.Label(form_frame, text='Parámetros', font=('TkDefaultFont', 14))
    title_form_label.pack(pady=10)

    # Mandatory fields.

    label_text = 'Selecciona la fuente de datos:'
    data_source_cb = form_fields.create_combobox_row(form_frame, label_text, self.data_sources, 
      default_option=self.data_sources[0], label_width=30, entry_width=35)

    label = 'Nombre de usuario:' 
    username_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    label = 'Contraseña:' 
    password_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35, show='*')

    label = 'Enlace de OPeNDAP:'
    opendap_link_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    # # TODO: Remove default values. This is only for testing purposes.
    # username_entry.insert(0, '')
    # password_entry.insert(0, '')
    # opendap_link_entry.insert(0, 'https://nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m')
    # lon_min_entry.insert(0, '-87.21394123899096')
    # lon_max_entry.insert(0, '-86.14119796245421')
    # lat_min_entry.insert(0, '20.216928148926932')
    # lat_max_entry.insert(0, '21.687290554990795')
    # depth_min_entry.insert(0, '0.49')
    # depth_max_entry.insert(0, '10')
    # start_date_entry.entry.delete(0, 'end')
    # start_date_entry.entry.insert(0, '2023-03-06')
    # end_date_entry.entry.delete(0, 'end')
    # end_date_entry.entry.insert(0, '2023-04-06')
    # variables_entry.insert(0, 'uo, vo')

    self.terms_status_var.set(False)
    terms_check = ttk.Checkbutton(
      form_frame, 
      text='Acepto los términos y condiciones', 
      variable=self.terms_status_var
    )
    terms_check.pack(fill='both', pady=(10, 0))

    # TODO: Test this btn. Remove the other fields above and the reference
    # in the callback. In the callback execute the connect method and
    # then display the fields based on the dataset structure.
    # Detect the lat, lon and depth dimension by axis=Y,X and Z.
    self.connect_button = ttk.Button(
      form_frame, 
      text='Conectar con respositorio', 
      state='enabled',
      command=lambda: self.__connect_data_source(
        data_source_cb.get(),
        username_entry.get(),
        password_entry.get(), 
        opendap_link_entry.get(),
        self.terms_status_var.get(),
      )
    )
    self.connect_button.pack(pady=(20, 0))

    self.form_frame = form_frame

    # Column 2

    column_2_frame = ttk.Frame(columns_frame)
    column_2_frame.grid(row=0, column=1, padx=20, pady=10, sticky='nsew')
    self.column_2_frame = column_2_frame

    map_frame = ttk.Frame(self.column_2_frame)
    map_frame.pack()
    self.map_frame = map_frame

    self.logging_console_frame = ttk.Frame(self.column_2_frame)
    self.logging_console_frame.pack()

    logging_console_title = ttk.Label(self.logging_console_frame, text='Mensajes del extractor', font=('TkDefaultFont', 14))
    logging_console_title.pack(pady=10)

    logging_console = ScrolledText(self.logging_console_frame, padding=5, height=25, autohide=True)
    logging_console.pack(fill=ttk_const.X, expand=ttk_const.YES)
    self.logging_console = logging_console

    # self.map_wrapper_frame = ttk.Frame(map_frame)
    # self.map_wrapper_frame.pack()
    # map_wrapper_frame = self.map_wrapper_frame

    # map_label = ttk.Label(map_wrapper_frame, text='Región seleccionada', font=('TkDefaultFont', 14))
    # map_label.pack(pady=10)

    # img_path = Path(ASSETS_DIR, 'images', 'map-example.png')
    # map_img = Image.open(img_path)
    # max_height = 600
    # original_width, original_height = map_img.size
    # new_width = int(original_width * max_height / original_height)
    # img_resized = map_img.resize((new_width, max_height), Image.ANTIALIAS)
    # self.map_img = ImageTk.PhotoImage(img_resized)
    # map_img_label = ttk.Label(map_wrapper_frame, image=self.map_img)
    # map_img_label.pack(pady=(10, 0))


  def __start_progress_bar(self):
    self.__progress_bar.start()


  def __stop_progress_bar(self):
    self.__progress_bar.stop()
  

  def __extraction_log_handler(self, message):
    print(message, end='', file=sys.stderr)
    self.logging_console.insert(ttk_const.END, message)
  

  def __connect_data_source(
    self,
    data_source: str, 
    username: str, 
    password: str, 
    opendap_link: str,
    accept_terms: bool
  ):
    print('------------- Connection info -----------------')
    print(f'Data source: {data_source}. Type: {type(data_source)}', file=sys.stderr)
    print(f'Username: {username}. Type: {type(username)}', file=sys.stderr)
    print(f'Password: {password}. Type: {type(password)}', file=sys.stderr)
    print(f'Opendap link: {opendap_link}. Type: {type(opendap_link)}', file=sys.stderr)
    print(f'Accept terms: {accept_terms}. Type: {type(accept_terms)}', file=sys.stderr)

    if self.dinamic_form_fields_frame:
      print('Destroying dinamic form fields frame.', file=sys.stderr)
      self.dinamic_form_fields_frame.pack_forget()
      self.dinamic_form_fields_frame.destroy()
      self.dinamic_form_fields_frame = None

    # Validations.
    if data_source == '' or opendap_link == '':
      tk.messagebox.showerror(title='Error', message='La fuente de datos y el enlace OPeNDAP son obligatorios.')
      return False
    if data_source not in self.data_sources:
      tk.messagebox.showerror(title='Error', message='Fuente de datos no válida.\n' 
          'Por favor seleccione una de las fuentes de datos disponibles.')
      return False
    if accept_terms == False:
      tk.messagebox.showerror(title='Error', message='Debe aceptar los términos y condiciones para continuar.')
      return False
    
    self.connect_button.configure(state='disabled')
    # Actual connection.
    # ['Copernicus', 'Otros - OPeNDAP']
    if data_source == 'Copernicus':
      self.extractor = CopernicusOpendapExtractor(
        opendap_url=opendap_link,
        auth=SimpleAuth(user=username, passwd=password),
        verbose=True)
    elif data_source == 'Otros - OPeNDAP':
      self.extractor = OpendapExtractor(
        opendap_url=opendap_link,
        auth=SimpleAuth(user=username, passwd=password),
        verbose=True)
    self.extractor.log_stream = self.log_stream
    # Display a message informing of this process.
    self.extractor.connect(
      success_callback=self.connect_success_callback,
      failure_callback=self.connect_failure_callback)
    self.__start_progress_bar()
  

  def connect_success_callback(self, extractor: OpendapExtractor):
    print(self.extractor.dataset, file=self.log_stream)
    self.__stop_progress_bar()
    self.connect_button.configure(state='enabled')
    # tk.messagebox.showinfo(
    #   title='Información de conexión',
    #   message='La conexión se estableció exitosamente.')
    # Display here the other fields.
    self.display_dimension_fields()


  def connect_failure_callback(self, err: BaseException):
    traceback.print_exception(err, file=self.log_stream)
    self.__stop_progress_bar()
    self.connect_button.configure(state='enabled')
    tk.messagebox.showerror(
      title='Información de conexión',
      message=f'Ocurrió un error durante la conexión: {type(err)}({err})')
  

  def display_dimension_fields(self):
    if not self.extractor:
      raise RuntimeError('Trying to display fields for dimensions but the extrator is missing.')
    if not self.extractor.dataset:
      raise RuntimeError('---- ERROR: Trying to display fields for dimensions but the dataset is missing.')
    # Updating dinamic form fields.
    if self.dinamic_form_fields_frame:
      print('Destroying dinamic form fields frame.', file=sys.stderr)
      self.dinamic_form_fields_frame.pack_forget()
      self.dinamic_form_fields_frame.destroy()
    print('Creating dinamic form fields frame.', file=sys.stderr)
    self.dinamic_form_fields_frame = ttk.Frame(self.form_frame)
    self.dinamic_form_fields_frame.pack()
    parent_frame = self.dinamic_form_fields_frame
    # Display instructions
    title_dims = ttk.Label(parent_frame, text='Delimita el subconjunto a descargar', font=('TkDefaultFont', 14))
    title_dims.pack(pady=10)
    # Display dataset volume.
    dataset_size_label = ttk.Label(parent_frame, text='Volúmen de datos:', font=('TkDefaultFont', 10))
    dataset_size_label.pack(pady=10)
    self.dataset_size_label = dataset_size_label
    # Display the dimension constraints form.
    dim_names = ext_wrangling.get_dims(self.extractor.dataset)
    self.dim_params = []
    for d in dim_names:
      use_default_display = False
      dim = self.extractor.dataset.coords[d]
      # Get pretty dim name and make labels.
      dname = d
      if 'long_name' in dim.attrs:
        dname = dim.attrs['long_name']
      label_min = f'{dname} min:'
      label_max = f'{dname} max:'
      # Check if is a standard axis.
      if 'axis' in dim.attrs:
        dim_axis = dim.attrs['axis']
        # TODO: Use an appropriate input type (text plain, combobox, date, etc)
        # TODO: Store a reference of the inputs and the dim name.
        # TODO: In the extract method parse the types if needed and try a dondload.
        # TODO: Think how the map is gona be created and gona use the zoom.
        if dim_axis == 'Y':
          # This is latitude dimension.
          print('Displaying fields for latitude', file=sys.stderr)
          lat_min_entry = form_fields.create_entry_row(parent_frame, label_min, label_width=30, entry_width=35)
          lat_max_entry = form_fields.create_entry_row(parent_frame, label_max, label_width=30, entry_width=35)
          # lat_min_entry.bind('<KeyRelease>', self.__coords_listenner)
          # lat_max_entry.bind('<KeyRelease>', self.__coords_listenner)
          lat_min_entry.bind('<KeyRelease>', self.__input_change_listenner)
          lat_max_entry.bind('<KeyRelease>', self.__input_change_listenner)
          lat_min_entry.insert(0, float(dim.min()))
          lat_max_entry.insert(0, float(dim.max()))
          self.dim_params.append(DimParam(
            dim_name=d,
            input_min=lat_min_entry,
            input_max=lat_max_entry,
            expected_type=float,
            dim_label=dname,
            expected_type_label='Números reales'))
          self.lat_min_entry = lat_min_entry
          self.lat_max_entry = lat_max_entry
        elif dim_axis == 'X':
          # This is longitude dimension.
          print('Displaying fields for longitude', file=sys.stderr)
          lon_min_entry = form_fields.create_entry_row(parent_frame, label_min, label_width=30, entry_width=35)
          lon_max_entry = form_fields.create_entry_row(parent_frame, label_max, label_width=30, entry_width=35)
          # lon_min_entry.bind('<KeyRelease>', self.__coords_listenner)
          # lon_max_entry.bind('<KeyRelease>', self.__coords_listenner)
          lon_min_entry.bind('<KeyRelease>', self.__input_change_listenner)
          lon_max_entry.bind('<KeyRelease>', self.__input_change_listenner)
          lon_min_entry.insert(0, float(dim.min()))
          lon_max_entry.insert(0, float(dim.max()))
          self.dim_params.append(DimParam(
            dim_name=d,
            input_min=lon_min_entry,
            input_max=lon_max_entry,
            expected_type=float,
            dim_label=dname,
            expected_type_label='Números reales'))
          self.lon_min_entry = lon_min_entry
          self.lon_max_entry = lon_max_entry
        elif dim_axis == 'Z':
          # This is depth/altitude dimension.
          print('Displaying fields for depth/altitude', file=sys.stderr)
          raw_dim_values = dim.values
          depths_data = list(np.round(raw_dim_values, 3))
          mapper = {}
          for i in range(len(depths_data)):
            mapper[ str(depths_data[i]) ] = raw_dim_values[i]
          depth_min_entry = form_fields.create_combobox_row(parent_frame, label_min, depths_data, 
            default_option=depths_data[0], label_width=30, entry_width=35)
          depth_max_entry = form_fields.create_combobox_row(parent_frame, label_max, depths_data, 
            default_option=depths_data[0], label_width=30, entry_width=35)
          depth_min_entry.bind('<<ComboboxSelected>>', self.__input_change_listenner)
          depth_max_entry.bind('<<ComboboxSelected>>', self.__input_change_listenner)
          self.dim_params.append(DimParam(
            dim_name=d,
            input_min=depth_min_entry,
            input_max=depth_max_entry,
            expected_type=float,
            dim_label=dname,
            expected_type_label='Números reales',
            mapper=mapper))
        elif dim_axis == 'T':
          # This is time dimension.
          print('Displaying fields for time', file=sys.stderr)
          dname = 'Time'
          label_min = f'{dname} min:'
          label_max = f'{dname} max:'
          start_date_entry = form_fields.create_date_entry_row(parent_frame, label_min, label_width=30)
          start_date_entry.entry.delete(0, 'end')
          start_date_entry.entry.insert(0, str(dim.min().values)[:10])
          end_date_entry = form_fields.create_date_entry_row(parent_frame, label_max, label_width=30)
          end_date_entry.entry.delete(0, 'end')
          end_date_entry.entry.insert(0, str(dim.max().values)[:10])
          start_date_entry.entry.bind('<KeyRelease>', self.__input_change_listenner)
          end_date_entry.entry.bind('<KeyRelease>', self.__input_change_listenner)
          start_date_entry.entry.bind('<FocusIn>', self.__input_change_listenner)
          end_date_entry.entry.bind('<FocusIn>', self.__input_change_listenner)
          self.dim_params.append(DimParam(
            dim_name=d,
            input_min=start_date_entry.entry,
            input_max=end_date_entry.entry,
            expected_type=str,
            dim_label=dname,
            expected_type_label='Texto con formato YYYY-MM-DD'))
        else:
          # Follow the netcdf standard for dimensions and search for a "axis" attribute.
          # If not presente in a coordinate, skip it.
          # use_default_display = True
          pass
      else:
        # Follow the netcdf standard for dimensions and search for a "axis" attribute.
        # If not presente in a coordinate, skip it.
        # use_default_display = True
        pass
      if use_default_display:
        # NOTE: This is not being used in favor to follow the netcdf standard.
        # None of the above matched even though they may were tested.
        print('Not a known axis. Displaying with default method.', file=sys.stderr)
        dim_min_entry = form_fields.create_entry_row(parent_frame, label_min, label_width=30, entry_width=35)
        dim_max_entry = form_fields.create_entry_row(parent_frame, label_max, label_width=30, entry_width=35)
        self.dim_params.append(DimParam(
          dim_name=d,
          input_min=dim_min_entry,
          input_max=dim_max_entry,
          expected_type=str,
          dim_label=dname,
          expected_type_label='Texto'))
    
    # Btn to redraw the map
    self.draw_map_button = ttk.Button(
      parent_frame, 
      text='Actualizar mapa',
      state='enabled',
      command=lambda: self.__update_map_manually()
    )
    self.draw_map_button.pack(pady=(20, 0))
    # Start drawing the map
    self.__update_map()
    # Display vars titles
    title_vars = ttk.Label(parent_frame, text='Selecciona las variables a descarcar', font=('TkDefaultFont', 14))
    title_vars.pack(pady=10)
    # Display the available variables
    var_names = ext_wrangling.get_vars(self.extractor.dataset)
    self.var_params = []
    for v in var_names:
      var = self.extractor.dataset[v]
      var_status = tk.BooleanVar(value=True)
      #var_status.set(True)
      var_long_name = ''
      label = v
      if 'long_name' in var.attrs:
        var_long_name = var.attrs['long_name']
        label = f'{v} - {var_long_name}'
      var_check = ttk.Checkbutton(
        parent_frame, 
        text=label, 
        variable=var_status
      )
      var_check.pack(fill='both', pady=(10, 0))
      self.var_params.append(VarParam(var_name=v, input=var_status))
      # var_check.bind('<ButtonRelease-1>', self.__input_change_listenner)
      var_status.trace_add('write', lambda *args: self.__input_change_listenner(args))
    
    # Input for dataset name
    label_ds_name = 'Nombre del archivo:'
    self.dataset_name_entry = form_fields.create_entry_row(parent_frame, label_ds_name, label_width=30, entry_width=35)
    
    # Btn to actually make the extraction.
    self.extract_button = ttk.Button(
      parent_frame, 
      text='Descargar datos',
      state='enabled',
      command=lambda: self.__start_extraction()
    )
    self.extract_button.pack(pady=(20, 0))
    self.__display_dataset_size()
  

  def __display_dataset_size(self):
    print('Trying to display dataset size', file=sys.stderr)
    if not self.dataset_size_label:
      return
    dim_constraints, err_title, err_message = self.__get_dim_constraints()
    if not dim_constraints:
      print(f'{err_title}: {err_message}', file=self.log_stream)
      self.dataset_size_label.configure(text=f'Se han seleccionado valores inválidos para las dimensiones.') #Volúmen de datos: No es posible determinar.
      # self.dataset_size_label.configure(text=err_message)
      return
    requested_vars = self.__get_requested_vars()
    if len(requested_vars) == 0:
      self.dataset_size_label.configure(text=f'No se ha seleccionado ninguna variable.')
      # self.dataset_size_label.configure(text=err_message)
      return
    print('Display dataset size. Dimensions:', dim_constraints, file=sys.stderr)
    self.extractor.dim_constraints = dim_constraints
    self.extractor.requested_vars = requested_vars
    self.extractor.verbose = True
    size = self.__get_adjusted_size()
    self.dataset_size_label.configure(text=f'Volúmen de datos: {np.round(size.size, 3)} {size.unit.name}')


  def __get_adjusted_size(self):
    size_unit_list = [
      SizeUnit.KILO_BYTE,
      SizeUnit.MEGA_BYTE,
      SizeUnit.GIGA_BYTE
    ]
    for size_unit in size_unit_list:
      size = self.extractor.get_size(size_unit)
      if size.size / 1024 <= 1 or SizeUnit.GIGA_BYTE == size_unit:
        return size


  def __coords_listenner(self, event):
    print('Coordinates changed.', event, file=sys.stderr)
    self.__update_map()
  

  def __input_change_listenner(self, event):
    self.__display_dataset_size()

  
  def __update_map_manually(self):
    lat_min, lat_max, lon_min, lon_max, able_to_draw, = self.__get_region()
    if able_to_draw:
      if lat_min > lat_max:
        tk.messagebox.showerror(
          title='No se puede actualizar el mapa',
          message=f'La latitud mínima no puede ser mayor que la latitud máxima.')
        return
      if lon_min > lon_max:
        tk.messagebox.showerror(
          title='No se puede actualizar el mapa',
          message=f'La longitud mínima no puede ser mayor que la longitud máxima.')
        return
      self.__draw_map(lat_min, lat_max, lon_min, lon_max)
    else:
      # Some fields may be missing or not be numbers.
      tk.messagebox.showerror(
        title='No se puede actualizar el mapa',
        message=f'Verifica que todos los campos de latitud y longitud tengan valores válidos (números reales).')
  

  def __update_map(self):
    lat_min, lat_max, lon_min, lon_max, able_to_draw, = self.__get_region()
    if able_to_draw:
      self.__draw_map(lat_min, lat_max, lon_min, lon_max)
    return able_to_draw
  

  def __get_region(self):
    lat_min = None
    lat_max = None
    lon_min = None
    lon_max = None
    able_to_draw_map = True
    if self.lat_min_entry:
      try:
        lat_min = float(self.lat_min_entry.get().strip())
      except:
        able_to_draw_map = False
    if self.lat_max_entry:
      try:
        lat_max = float(self.lat_max_entry.get().strip())
      except:
        able_to_draw_map = False
    if self.lon_min_entry:
      try:
        lon_min = float(self.lon_min_entry.get().strip())
      except:
        able_to_draw_map = False
    if self.lon_max_entry:
      try:
        lon_max = float(self.lon_max_entry.get().strip())
      except:
        able_to_draw_map = False
    return lat_min, lat_max, lon_min, lon_max, able_to_draw_map


  def __draw_map(self, lat_min, lat_max, lon_min, lon_max):
    region_map_builder = StaticRegionMapBuilder(
      amplitude=0,
      lon_dim_min=lon_min,
      lon_dim_max=lon_max,
      lat_dim_min=lat_min,
      lat_dim_max=lat_max,
      verbose=True)
    region_map_builder.build(
      success_callback=self.__region_map_success,
      failure_callback=self.__region_map_failure)
    if self.draw_map_button:
      print('Disabling btn to draw the map')
      self.draw_map_button.configure(state='disabled')


  # TODO: Test this
  def __region_map_success(self, chart_builder: ChartBuilder):
    if self.draw_map_button:
      print('Enabling btn to draw the map')
      self.draw_map_button.configure(state='enabled')
    # img_path = Path(ASSETS_DIR, 'images', 'map-example-2.png')
    # Destroy the frame.
    if self.map_wrapper_frame:
      self.map_wrapper_frame.pack_forget()
      self.map_wrapper_frame.destroy()
    # Re create the frame.
    self.map_wrapper_frame = ttk.Frame(self.map_frame)
    self.map_wrapper_frame.pack()
    map_wrapper_frame = self.map_wrapper_frame

    map_label = ttk.Label(map_wrapper_frame, text='Región seleccionada', font=('TkDefaultFont', 14))
    map_label.pack(pady=10)

    # img_path = Path(ASSETS_DIR, 'images', 'map-example-2.png')
    map_img = Image.open(chart_builder._chart.get_buffer())
    max_width = 800 
    original_width, original_height = map_img.size
    new_height = int(original_height * max_width / original_width) 
    img_resized = map_img.resize((max_width, new_height), Image.ANTIALIAS) 
    self.map_img = ImageTk.PhotoImage(img_resized)
    map_img_label = ttk.Label(map_wrapper_frame, image=self.map_img)
    map_img_label.pack(pady=(10, 0))


  def __region_map_failure(self, err: BaseException):
    traceback.print_exception(err, file=self.log_stream)
    if self.draw_map_button:
      print('Enabling btn to draw the map')
      self.draw_map_button.configure(state='enabled')
    tk.messagebox.showerror(
      title='Información de conexión',
      message=f'Ocurrió un error durante la conexión: {type(err)}({err})')


  def __start_extraction(self):
    try:
      self.__setup_extraction()
    except BaseException as err:
      traceback.print_exception(err, file=self.log_stream)
      tk.messagebox.showerror(
        title='Información de descarga',
        message=f'Ocurrió un error al iniciar el proceso de descarga: {type(err)}({err})')
      self.extract_button.configure(state='enabled')
      self.connect_button.configure(state='enabled')
      self.draw_map_button.configure(state='enabled')   


  def __setup_extraction(self):
    print('------------------------------')
    for dim_param in self.dim_params:
      min_val = dim_param.get_min_val(parse=False)
      max_val = dim_param.get_max_val(parse=False)
      print(f'{dim_param.dim_name} [ {min_val} ({type(min_val)}), {max_val} ({type(max_val)}) ] expected type: {dim_param.expected_type}')

    for var_param in self.var_params:
      print(f'{var_param.var_name}: {var_param.input.get()}', file=sys.stderr)
    
    # Dim validations and dim constraints construction
    dim_constraints, err_title, err_message = self.__get_dim_constraints()
    print(f'Dimension constraints: {dim_constraints}', file=self.log_stream)
    if not dim_constraints:
      tk.messagebox.showerror(title=err_title, message=err_message)
      return

    dataset_name = self.dataset_name_entry.get().strip()
    if dataset_name == '':
      tk.messagebox.showerror(
        title='Validaciones extra',
        message=f'El nombre del archivo resultante no puede estar vacío.')
      return

    # Extraccion de datos.
    # def show_log(data):
    #   print(data, end='', file=sys.stderr)
    # log_stream = LogStream(callback=show_log)

    requested_vars = self.__get_requested_vars()
    print('Requested var list:', requested_vars, file=self.log_stream)

    if len(requested_vars) == 0:
      tk.messagebox.showerror(
        title='Validaciones de variables',
        message=f'No se ha seleccionado ninguna variable para descargar, por favor seleccione al menos una.')
      return

    self.extractor.dim_constraints = dim_constraints
    self.extractor.requested_vars = requested_vars
    # self.extractor.log_stream = self.log_stream
    self.extractor.verbose = True

    curr_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'Starting extraction at: {curr_datetime}', file=self.log_stream)
    timestamp = "".join(str(datetime.now().timestamp()).split('.'))
    filename = f'{dataset_name}_{timestamp}.nc'
    fpath = Path(HOME_DATASETS_DIR, filename)
    self.extractor.extract(
      fpath,
      success_callback=self.__success_extract_callback,
      failure_callback=self.__failure_extract_callback)
    self.extract_button.configure(state='disabled')
    self.connect_button.configure(state='disabled')
    self.draw_map_button.configure(state='disabled')
    self.__start_progress_bar()

    size_result = self.extractor.get_size(SizeUnit.MEGA_BYTE)
    tk.messagebox.showinfo(
      title='Información de descarga',
      message=f'Se ha iniciado la descarga. Por favor sé paciente, el volúmen de datos es de: {np.round(size_result.size, 3)} {size_result.unit.name}')
  
  
  def __success_extract_callback(self, extract_details: ExtractionDetails):
    self.extract_button.configure(state='enabled')
    self.connect_button.configure(state='enabled')
    self.draw_map_button.configure(state='enabled')
    self.__stop_progress_bar()
    print('Extraction details:', extract_details, file=self.log_stream)
    fpath = Path(extract_details.file.path)
    tk.messagebox.showinfo(
      title='Información de descarga',
      message=f'La descarga terminó con éxito. Puede encontrar el dataset en: {fpath.resolve()}')


  def __failure_extract_callback(self, err: BaseException):
    traceback.print_exception(err, file=self.log_stream)
    self.connect_button.configure(state='enabled')
    self.extract_button.configure(state='enabled')
    self.draw_map_button.configure(state='enabled')
    self.__stop_progress_bar()
    tk.messagebox.showerror(
      title='Información de descarga',
      message=f'Ocurrió un error durante la descarga: {type(err)}({err})')


  # TODO: Finish validation
  def __get_dim_constraints(self) -> tuple[dict[str, slice], str, str]:
    dim_constraints = {}
    for dim_param in self.dim_params:
      print(f'dim: {dim_param.dim_name}', file=sys.stderr)
      dim_min_val = None
      dim_max_val = None
      try:
        dim_min_val = dim_param.get_min_val()
        print(f'min_val: {dim_min_val} ({type(dim_min_val)})', file=sys.stderr)
      except ValueError as err:
        title='Validación de dimensiones',
        message=f'El campo "{dim_param.dim_label} min" espera valores de tipo "{dim_param.expected_type_label}", pero obtuvo el valor "{dim_param.get_min_val(parse=False)}": {type(err)}({err})'
        return None, title, message
      try:
        dim_max_val = dim_param.get_max_val()
        print(f'max_val: {dim_max_val} ({type(dim_max_val)})', file=sys.stderr)
      except ValueError as err:
        title='Validación de dimensiones',
        message=f'El campo "{dim_param.dim_label} max" espera valores de tipo "{dim_param.expected_type_label}", pero obtuvo el valor "{dim_param.get_min_val(parse=False)}": {type(err)}({err})'
        return None, title, message
      if dim_min_val is None and dim_max_val is None:
        continue
      if dim_min_val is None or dim_max_val is None:
        title='Validación de dimensiones',
        message=f'Para la dimensión {dim_param.dim_label} el valor mínimo y máximo deben estar dados o bien ambos deben omitirse.'
        return None, title, message
      if dim_min_val > dim_max_val:
        title='Validación de dimensiones',
        message=f'Para la dimensión {dim_param.dim_label} el valor mínimo no puede ser mayor que el valor máximo.'
        return None, title, message

      dim = self.extractor.dataset.coords[dim_param.dim_name]
      if 'axis' in dim.attrs:
        dim_axis = dim.attrs['axis']
        # This is latitude and longitude dimensions.
        if dim_axis == 'Y' or dim_axis == 'X':
          ds_dim_min = float(dim.min())
          ds_dim_max = float(dim.max())
          if dim_min_val < ds_dim_min:
            title='Validación de dimensiones',
            message=f'Para la dimensión {dim_param.dim_label} se ingreso un valor mínimo inferior al del dataset de {ds_dim_min}.'
            return None, title, message
          if dim_max_val > ds_dim_max:
            title='Validación de dimensiones',
            message=f'Para la dimensión {dim_param.dim_label} se ingreso un valor máximo superior al del dataset de {ds_dim_max}.'
            return None, title, message
        elif dim_axis == 'T':
          # This is time dimension.
          try:
            datetime.strptime(dim_min_val, '%Y-%m-%d').date()
            datetime.strptime(dim_max_val, '%Y-%m-%d').date()
          except:
            title='Error', 
            message='Las fechas deben tener un formato "YYYY-MM-DD" válido.'
            return None, title, message
          ds_dim_min = str(dim.min().values)[:10]
          ds_dim_max = str(dim.max().values)[:10]
          if dim_min_val < ds_dim_min:
            title='Validación de dimensiones',
            message=f'Para la dimensión {dim_param.dim_label} se ingreso un valor mínimo inferior al del dataset de {ds_dim_min}.'
            return None, title, message
          if dim_max_val > ds_dim_max:
            title='Validación de dimensiones',
            message=f'Para la dimensión {dim_param.dim_label} se ingreso un valor máximo superior al del dataset de {ds_dim_max}.'
            return None, title, message

      dim_constraints[dim_param.dim_name] = slice(dim_min_val, dim_max_val)

    return dim_constraints, '', ''
  

  def __get_requested_vars(self):
    return [var_param.var_name for var_param in self.var_params if var_param.input.get()]
