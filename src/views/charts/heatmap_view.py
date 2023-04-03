import pathlib
import tkinter as tk
import ttkbootstrap as ttk
import utils.dataset_utils as dataset_utils
import utils.global_variables as global_vars
import utils.basic_form_fields as form_fields
from views.templates.tab_view import TabView
from omdepplotlib.chart_building import level_chart
from PIL import ImageTk, Image
from datetime import datetime

class HeatMapView(TabView):
  def __init__(self, master):
    super().__init__(master, chart_type='HEATMAP')
    self.__build_method = None
    self.__static_build_method_frame = None
    self.__animated_build_method_frame = None

    self.variable_list = dataset_utils.get_variables()
    self.depth_list = dataset_utils.get_depth_values()
    self.duration_unit_dict = {
      'Frames por segundo': 'FRAMES_PER_SECOND',
      'Segundos por frame': 'SECONDS_PER_FRAME'
    }

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

    title_view_label = ttk.Label(self.col2_user_params_frame, text='Heatmap', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=10)

    # Form.
    form_frame = ttk.Frame(self.col2_user_params_frame, bootstyle='default')
    form_frame.pack(fill='x', padx=20, pady=10)

    form_entries_frame = ttk.Frame(form_frame)
    form_entries_frame.pack(fill='x')

    label_text = 'Método de construcción:'
    build_method_list = ['Estático', 'Animado']
    build_method_cb = form_fields.create_combobox_row(form_entries_frame, label_text, build_method_list)
    build_method_cb.bind("<<ComboboxSelected>>", self.__selected_build_method_handler)

    label_text = 'Variable:'
    variable_cb = form_fields.create_combobox_row(form_entries_frame, label_text, self.variable_list)

    label_text = 'Profundidad [m]:'
    default_depth = self.depth_list[0]
    depth_cb = form_fields.create_combobox_row(form_entries_frame, label_text, self.depth_list, default_option=default_depth)

    label_text = 'Título del gráfico:'
    chart_title_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Paleta de colores:'
    palette_colors_list = ['OrRd', 'plasma', 'Greens', 'viridis']
    palette_colors_cb = form_fields.create_combobox_row(form_entries_frame, label_text, palette_colors_list)

    # Following entries will be hidden or shown depending on the selected build method.

    self.__static_build_method_frame = ttk.Frame(form_entries_frame)
    self.__static_build_method_frame.pack_forget()
    label_text = 'Fecha objetivo:'
    target_date_entry = form_fields.create_date_entry_row(self.__static_build_method_frame, label_text)

    self.__animated_build_method_frame = ttk.Frame(form_entries_frame)
    self.__animated_build_method_frame.pack_forget()
    label_text = 'Unidad de duración:'
    duration_unit_list = list(self.duration_unit_dict.keys())
    duration_cb = form_fields.create_combobox_row(self.__animated_build_method_frame, label_text, duration_unit_list)
    label_text = 'Duración'
    duration_entry = form_fields.create_entry_row(self.__animated_build_method_frame, label_text)
    label_text = 'Fecha de inicio:'
    start_date_entry = form_fields.create_date_entry_row(self.__animated_build_method_frame, label_text)
    label_text = 'Fecha de fin:'
    end_date_entry = form_fields.create_date_entry_row(self.__animated_build_method_frame, label_text)


    # Apply button.
    connect_button = ttk.Button(
      form_frame, 
      text='Generar gráfico', 
      command=lambda: self.__start_creation_chart(
        build_method_cb.get(),
        variable_cb.get(), depth_cb.get(),
        chart_title_entry.get(), palette_colors_cb.get(),
        target_date=target_date_entry.entry.get(), # Only for static build method.
        duration_unit=duration_cb.get(), duration=duration_entry.get(), # Only for animated build method.
        start_date=start_date_entry.entry.get(), end_date=end_date_entry.entry.get() # Only for animated build method.
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

    # TODO: Display image in scroll_frame (hide by default?).
    # TODO: Display info about dataset in scroll_frame (hide by default).

  def __start_creation_chart(
    self,
    build_method,
    variable,
    depth,
    chart_title,
    palette_colors,
    target_date=None,
    duration_unit=None,
    duration=None,
    start_date=None,
    end_date=None
  ):
    print('-----------------------------')
    print(f'build_method: "{build_method}"')
    print(f'variable: "{variable}"')
    print(f'depth: "{depth}"')
    print(f'chart_title: "{chart_title}"')
    print(f'palette_colors: "{palette_colors}"')
    print(f'target_date: "{target_date}"')
    print(f'duration_unit: "{duration_unit}"')
    print(f'duration: "{duration}"')
    print(f'start_date: "{start_date}"')
    print(f'end_date: "{end_date}"')

    self.__show_and_run_progress_bar()
    self.chart_and_btns_frame.pack_forget()

    valid_fields = self.__fields_validation(build_method, variable, depth, chart_title, 
      palette_colors, target_date, duration_unit, duration, start_date, end_date)
    if not valid_fields:
      return

    try:
      dataset = global_vars.current_project_dataset
      self.chart_builder = level_chart.HeatMapBuilder(dataset=dataset)
      if self.__build_method == 'static':
        self.__generate_static_chart(variable, depth, chart_title, palette_colors,
          target_date)
      elif self.__build_method == 'animated':
        self.__generate_animated_chart(variable, depth, chart_title, palette_colors,
          duration_unit, duration, start_date, end_date)

      self.__stop_and_hide_progress_bar()
      self.chart_and_btns_frame.pack(fill='both', expand=1)
    except:
      pass

  def __generate_static_chart(
    self,
    variable,
    depth,
    chart_title,
    palette_colors,
    target_date
  ):
    dim_constraints = {
      'time': [target_date],
      'depth': [depth]
    }
    if variable == 'zos':
      dim_constraints = {
        'time': [target_date]
      }
    print(f'-> Heatmap static image for "{variable}" variable.')
    self.chart_builder.build_static(
      var_name=variable,
      title=chart_title,
      var_label=self.plot_measure_label[variable],
      dim_constraints=dim_constraints,
      lat_dim_name='latitude', # TODO: Revisar si el usuario tendre que ingresar esto.
      lon_dim_name='longitude', # TODO: Revisar si el usuario tendre que ingresar esto.
      color_palette=palette_colors
    )

    img_buffer = self.chart_builder._chart.get_buffer()
    self.chart_img = ImageTk.PhotoImage(Image.open(img_buffer))
    self.chart_img_label.configure(image=self.chart_img)
    # Hide button to play gif.
    self.play_chart_btn.pack_forget()

  def __generate_animated_chart(
    self,
    variable,
    depth,
    chart_title,
    palette_colors,
    duration_unit,
    duration,
    start_date,
    end_date
  ):
    print(f'-> Heatmap gif for "{variable}" variable.')
    dim_constraints = {
      'depth': [depth],
      'time': slice(start_date, end_date)
    }
    if variable == 'zos':
      dim_constraints = {}

    duration_unit = self.duration_unit_dict[duration_unit]
    duration = int(duration) if duration_unit == 'FRAMES_PER_SECOND' else round(float(duration), 2)

    try:
      self.chart_builder.build_animation(
        var_name=variable,
        title=chart_title,
        var_label=self.plot_measure_label[variable],
        dim_constraints=dim_constraints,
        time_dim_name='time',
        lat_dim_name='latitude',
        lon_dim_name='longitude',
        duration=duration,
        duration_unit=duration_unit,
        color_palette=palette_colors
      )
    except:
      message = 'Rango de fechas no válido. Revise la información del '
      message += 'dataset respecto al rango de fechas y su resolución temporal.'
      tk.messagebox.showerror(title='Error', message=message)
      raise ValueError('Rango de fechas no válido')

    gif_buffer = self.chart_builder._chart.get_buffer()
    self.gif_images = self.get_gif_frames(gif_buffer)
    self.num_frames = len(self.gif_images)
    self.current_frame = 0
    if duration_unit == 'SECONDS_PER_FRAME':
      self.gif_frame_duration_ms = round(duration * 1000)
    elif duration_unit == 'FRAMES_PER_SECOND':
      self.gif_frame_duration_ms = round(1000 / duration)
    # Show first frame
    self.chart_img = self.gif_images[0]
    self.chart_img_label.configure(image=self.chart_img)
    # Show button to play gif.
    self.play_chart_btn.pack()

  def __fields_validation(
    self, 
    build_method, 
    variable, 
    depth, 
    chart_title, 
    palette_colors,
    target_date=None,
    duration_unit=None,
    duration=None,
    start_date=None,
    end_date=None
  ):
    chart_title = chart_title.strip()
    
    empty_fields = []
    if build_method == '': empty_fields.append('Método de construcción')
    if variable == '': empty_fields.append('Variable')
    if depth == '': empty_fields.append('Profundidad')
    if chart_title == '': empty_fields.append('Título del gráfico')
    if palette_colors == '': empty_fields.append('Paleta de colores')

    if self.__build_method == 'static':
      if target_date == '' or target_date == None:
        empty_fields.append('Fecha de objetivo')
      try:
        target_date = datetime.strptime(target_date, '%Y-%m-%d')
      except:
        message = 'La fecha objetivo debe tener el formato "YYYY-MM-DD".'
        tk.messagebox.showerror(title='Error', message=message)
        return False
    elif self.__build_method == 'animated':
      if duration_unit == '' or duration_unit == None:
        empty_fields.append('Unidad de duración')

      duration = duration.strip()
      if duration == '' or duration == None:
        empty_fields.append('Duración')
      else:
        if self.duration_unit_dict[duration_unit] == 'FRAMES_PER_SECOND':
          try:
            duration = int(duration)
            if duration <= 0 or duration > 24:
              raise Exception
          except:
            message = 'La duración debe ser un número entero entre 1 y 24, '
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

      if start_date == '' or start_date == None:
        empty_fields.append('Fecha inicial')
      if end_date == '' or end_date == None:
        empty_fields.append('Fecha final')
      try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
      except:
        message = 'Las fechas deben tener el formato "YYYY-MM-DD".'
        tk.messagebox.showerror(title='Error', message=message)
        return False
      if start_date >= end_date:
        message = 'La fecha inicial debe ser menor a la fecha final.'
        tk.messagebox.showerror(title='Error', message=message)
        return False

      dataset_date_values = dataset_utils.get_time_values()
      min_dataset_date = dataset_date_values[0].date()
      max_dataset_date = dataset_date_values[-1].date()
      if end_date < min_dataset_date or start_date > max_dataset_date:
        message = 'Las fechas deben estar dentro del rango de fechas del dataset. '
        message += f'El rango de fechas del dataset va del {min_dataset_date} hasta el {max_dataset_date}.'
        tk.messagebox.showerror(title='Error', message=message)
        return False

    if len(empty_fields) > 0:
      message = 'Todos los campos son obligatorios. Datos faltantes: \n'
      message += ', '.join(empty_fields)
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

  def __show_and_run_progress_bar(self):
    # print('se llamo a show progress bar')
    self.__progress_bar.pack(pady=10)
    self.__progress_bar.start()

  def __stop_and_hide_progress_bar(self):
    pass
    # print('se llamo a stop and hide progress bar')
    # self.__progress_bar.stop()
    # self.__progress_bar.pack_forget()
