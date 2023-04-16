# NOTE: Temporary view. Reused dowload_data_view.py. This was updated in mockups.
import tkinter as tk
import ttkbootstrap as ttk
import inspect
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip
from pathlib import Path
from datetime import datetime
from PIL import ImageTk, Image
from utils.global_constants import HOME_DATASETS_DIR, ASSETS_DIR
import utils.basic_form_fields as form_fields
from views.templates.scrollable_view import ScrollableView
from siaextractlib.utils.log import LogStream
from siaextractlib.utils.auth import SimpleAuth
from siaextractlib.extractors import OpendapExtractor

class DataExtractorView(ScrollableView):
  def __init__(self, master):
    super().__init__(master)
    self.data_sources = ['Copernicus', 'HYCOM']
    self.terms_status_var = tk.BooleanVar()
    self.map_img = None

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    title_view_label = ttk.Label(self.scroll_frame, text='Descarga de datos', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=10)

    columns_frame = ttk.Frame(self.scroll_frame)
    columns_frame.pack()

    # Column 1

    form_frame = ttk.Frame(columns_frame)
    form_frame.grid(row=0, column=0, padx=20, pady=10, sticky='nsew')

    title_form_label = ttk.Label(form_frame, text='Parámetros', font=('TkDefaultFont', 14))
    title_form_label.pack(pady=10)

    label_text = 'Selecciona la fuente de datos:'
    data_source_cb = form_fields.create_combobox_row(form_frame, label_text, self.data_sources, 
      default_option=self.data_sources[0], label_width=30, entry_width=35)

    label = 'Nombre de usuario:' 
    username_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    label = 'Contraseña:' 
    password_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35, show='*')

    label = 'Enlace de OPeNDAP:'
    opendap_link_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    label = 'Longitud mínima:'
    lon_min_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    label = 'Longitud máxima:'
    lon_max_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    label = 'Latitud mínima:'
    lat_min_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    label = 'Latitud máxima:'
    lat_max_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    label = 'Profundidad mínima:'
    depth_min_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    label = 'Profundidad máxima:'
    depth_max_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    label = 'Fecha de inicio:'
    start_date_entry = form_fields.create_date_entry_row(form_frame, label, label_width=30)

    label = 'Fecha de fin:'
    end_date_entry = form_fields.create_date_entry_row(form_frame, label, label_width=30)

    label = 'Variables:'
    variables_entry = form_fields.create_entry_row(form_frame, label, label_width=30, entry_width=35)

    # TODO: Remove default values. This is only for testing purposes.
    username_entry.insert(0, 'amontejo')
    password_entry.insert(0, 'MyCopernicusAccount25;')
    opendap_link_entry.insert(0, 'https://nrt.cmems-du.eu/thredds/dodsC/cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m')
    lon_min_entry.insert(0, '-87.21394123899096')
    lon_max_entry.insert(0, '-86.14119796245421')
    lat_min_entry.insert(0, '20.216928148926932')
    lat_max_entry.insert(0, '21.687290554990795')
    depth_min_entry.insert(0, '0.49')
    depth_max_entry.insert(0, '10')
    start_date_entry.entry.delete(0, 'end')
    start_date_entry.entry.insert(0, '2023-03-06')
    end_date_entry.entry.delete(0, 'end')
    end_date_entry.entry.insert(0, '2023-04-06')
    variables_entry.insert(0, 'uo, vo')

    self.terms_status_var.set(False)
    terms_check = ttk.Checkbutton(
      form_frame, 
      text='Acepto los términos y condiciones', 
      variable=self.terms_status_var
    )
    terms_check.pack(fill='both', pady=(10, 0))

    connect_button = ttk.Button(
      form_frame, 
      text='Descargar datos', 
      command=lambda: self.__start_extraction(
        data_source_cb.get(), username_entry.get(),
        password_entry.get(), 
        opendap_link_entry.get(),
        lon_min_entry.get(), lon_max_entry.get(),
        lat_min_entry.get(), lat_max_entry.get(),
        depth_min_entry.get(), depth_max_entry.get(),
        start_date_entry.entry.get(), end_date_entry.entry.get(),
        variables_entry.get(),
        self.terms_status_var.get(),
      )
    )
    connect_button.pack(pady=(20, 0))

    # Column 2

    map_frame = ttk.Frame(columns_frame)
    map_frame.grid(row=0, column=1, padx=20, pady=10, sticky='nsew')

    map_label = ttk.Label(map_frame, text='Región seleccionada', font=('TkDefaultFont', 14))
    map_label.pack(pady=10)

    img_path = Path(ASSETS_DIR, 'images', 'map-example.png')
    map_img = Image.open(img_path)
    max_height = 600
    original_width, original_height = map_img.size
    new_width = int(original_width * max_height / original_height)
    img_resized = map_img.resize((new_width, max_height), Image.ANTIALIAS)
    self.map_img = ImageTk.PhotoImage(img_resized)
    map_img_label = ttk.Label(map_frame, image=self.map_img)
    map_img_label.pack(pady=(10, 0))

  def __start_extraction(
    self, 
    data_source, 
    username, 
    password, 
    opendap_link,
    lon_min, lon_max,
    lat_min, lat_max,
    depth_min, depth_max,
    start_date, end_date,
    variables,
    accept_terms,
  ):
    print('------------------------------')
    print(f'Data source: {data_source}. Type: {type(data_source)}')
    print(f'Username: {username}. Type: {type(username)}')
    print(f'Password: {password}. Type: {type(password)}')
    print(f'Opendap link: {opendap_link}. Type: {type(opendap_link)}')
    print(f'Lon min: {lon_min}. Type: {type(lon_min)}')
    print(f'Lon max: {lon_max}. Type: {type(lon_max)}')
    print(f'Lat min: {lat_min}. Type: {type(lat_min)}')
    print(f'Lat max: {lat_max}. Type: {type(lat_max)}')
    print(f'Depth min: {depth_min}. Type: {type(depth_min)}')
    print(f'Depth max: {depth_max}. Type: {type(depth_max)}')
    print(f'Start date: {start_date}. Type: {type(start_date)}')
    print(f'End date: {end_date}. Type: {type(end_date)}')
    print(f'Variables: {variables}. Type: {type(variables)}')
    print(f'Accept terms: {accept_terms}. Type: {type(accept_terms)}')

    is_valid = self.__form_validation(
      data_source, username, password, opendap_link, lon_min, lon_max, lat_min, lat_max, 
      depth_min, depth_max, start_date, end_date, variables, 
      accept_terms
    )
    if not is_valid:
      return

    # Conversion de datos
    lon_min = float(lon_min)
    lon_max = float(lon_max)
    lat_min = float(lat_min)
    lat_max = float(lat_max)
    depth_min = float(depth_min)
    depth_max = float(depth_max)
    variables = variables.split(',')
    variables = [var.strip() for var in variables]

    # Extraccion de datos.
    print(f'---- Starting: {inspect.currentframe().f_code.co_name}')
    def show_log(data):
      print(data, end='')
    log_stream = LogStream(callback=show_log)

    extractor = OpendapExtractor(
      opendap_url=opendap_link,
      auth=SimpleAuth(user=username, passwd=password),
      # TODO: Get name of dimensions from dataset.
      dim_constraints={
        'time': slice(start_date, end_date),
        'depth': slice(depth_min, depth_max),
        'longitude': slice(lon_min, lon_max),
        'latitude': slice(lat_min, lat_max)
      },
      requested_vars=variables,
      log_stream=log_stream,
      verbose=True)
    
    curr_datetime = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    filename = f'dataset_{curr_datetime}.nc'
    extract_details = extractor.sync_connect().sync_extract(Path(HOME_DATASETS_DIR, filename))
    print(extract_details)
    extractor.close_connect()


    tk.messagebox.showinfo(title='Información', message='La descarga de datos se realizo con éxito.')

  # TODO: Finish validation
  def __form_validation(
    self, 
    data_source, 
    username, 
    password, 
    opendap_link,
    lon_min, lon_max,
    lat_min, lat_max,
    depth_min, depth_max,
    start_date, end_date,
    variables,
    accept_terms,
  ):
    # Validate data.
    if data_source == '' or username == '' or password == '':
      tk.messagebox.showerror(title='Error', message='Todos los campos son obligatorios.')
      return False
    if data_source not in self.data_sources:
      tk.messagebox.showerror(title='Error', message='Fuente de datos no válida.\n' 
          'Por favor seleccione una de las fuentes de datos disponibles.')
      return False
    if accept_terms == False:
      tk.messagebox.showerror(title='Error', message='Debe aceptar los términos y condiciones.')
      return False

    return True