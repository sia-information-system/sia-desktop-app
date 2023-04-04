import pathlib
import tkinter as tk
import ttkbootstrap as ttk
import utils.dataset_utils as dataset_utils
import utils.global_variables as global_vars
import utils.basic_form_fields as form_fields
from datetime import datetime
from views.templates.tab_view import TabView
from omdepplotlib.chart_building import level_chart
from PIL import ImageTk, Image

class CurrentsChartView(TabView):
  def __init__(self, master):
    super().__init__(master, chart_type='CURRENTS_CHART')
    self.depth_list = dataset_utils.get_depth_values()

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
    depth_cb = form_fields.create_combobox_row(form_entries_frame, label_text, self.depth_list, default_option=default_depth)

    label_text = 'Título del gráfico:'
    chart_title_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    label_text = 'Fecha objetivo:'
    target_date_entry = form_fields.create_date_entry_row(form_entries_frame, label_text)

    label_text = 'Densidad de la flecha:'
    stride_entry = form_fields.create_entry_row(form_entries_frame, label_text)

    # Apply button.
    connect_button = ttk.Button(
      form_frame, 
      text='Generar gráfico', 
      command=lambda: self.__start_creation_chart(
        depth_cb.get(),
        chart_title_entry.get(),
        target_date_entry.entry.get(),
        stride_entry.get()
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
    depth,
    chart_title,
    target_date,
    stride
  ):
    print('-----------------------------')
    print(f'depth: "{depth}"')
    print(f'chart_title: "{chart_title}"')
    print(f'target_date: "{target_date}"')
    print(f'stride: "{stride}"')

    self.__show_and_run_progress_bar()
    self.chart_and_btns_frame.pack_forget()

    valid_fields = self.__fields_validation(depth, chart_title, target_date, stride)
    if not valid_fields:
      return

    try:
      dataset = global_vars.current_project_dataset 
      self.chart_builder = level_chart.ArrowChartBuilder(dataset=dataset)

      self.__generate_static_chart(depth, chart_title, target_date, stride)

      self.__stop_and_hide_progress_bar()
      self.chart_and_btns_frame.pack(fill='both', expand=1)
    except Exception as e:
      print(f'Error: {e}')
      pass

  def __generate_static_chart(
    self,
    depth,
    chart_title,
    target_date,
    stride
  ):    
    dim_constraints = {
      'time': [target_date],
      'depth': depth,
    }

    print(f'-> Static Arror chart image.')
    self.chart_builder.build_static(
      var_ew = 'uo', # TODO: Solicitar al usuario.
      var_nw = 'vo', # TODO: Solicitar al usuario.
      var_lon = 'longitude', # TODO: Solicitar al usuario.
      var_lat = 'latitude', # TODO: Solicitar al usuario.
      title = chart_title,
      dim_constraints= dim_constraints,
      stride = int(stride)
    )

    img_buffer = self.chart_builder._chart.get_buffer()
    img = Image.open(img_buffer)
    img_resized = self.resize_chart_img(img)
    self.chart_img = ImageTk.PhotoImage(img_resized)
    self.chart_img_label.configure(image=self.chart_img)
    # Hide button to play gif.
    self.play_chart_btn.pack_forget()

  def __fields_validation(
    self, 
    depth, 
    chart_title,
    target_date,
    stride
  ):
    chart_title = chart_title.strip()
    
    # Empty fields validation.
    empty_fields = []
    if chart_title == '': empty_fields.append('Título del gráfico')
    if depth == '': empty_fields.append('Profundidad')
    if target_date == '': empty_fields.append('Fecha objetivo')
    if stride == '': empty_fields.append('Densidad de la flecha')

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
      message = 'Densidad de la flecha debe ser un número entero positivo.'
      tk.messagebox.showerror(title='Error', message=message)
      return False

    # Validate target date format.
    try:
      target_date = datetime.strptime(target_date, '%Y-%m-%d')
    except:
      message = 'La fecha objetivo debe tener el formato "YYYY-MM-DD".'
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
