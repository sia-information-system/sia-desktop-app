import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.tooltip import ToolTip
from views.templates.scrollable_view import ScrollableView

class HeatMapView(ScrollableView):
  def __init__(self, master):
    super().__init__(master)
    self.__build_method = None
    self.__static_build_method_frame = None
    self.__animated_build_method_frame = None

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    # ------------------ Elements of the view  ------------------

    title_view_label = ttk.Label(self.scroll_frame, text='Heatmap', font=('Helvetica', 14))
    title_view_label.pack(pady=10)

    # Form.
    form_frame = ttk.Frame(self.scroll_frame, bootstyle='default')
    form_frame.pack(fill='x', padx=100, pady=10)

    form_entries_frame = ttk.Frame(form_frame)
    form_entries_frame.pack(fill='x')

    label_text = 'Dataset a utilizar:'
    datasets_list = ['foo', 'bar', 'baz']
    datasets_cb = self.__create_combobox_row(form_entries_frame, label_text, datasets_list)

    label_text = 'Método de construcción:'
    build_method_list = ['Estático', 'Animado']
    build_method_cb = self.__create_combobox_row(form_entries_frame, label_text, build_method_list)
    build_method_cb.bind("<<ComboboxSelected>>", self.__selected_build_method_handler)

    label_text = 'Variable:'
    variable_list = ['thetao', 'vo', 'uo', 'so', 'zos']
    variable_cb = self.__create_combobox_row(form_entries_frame, label_text, variable_list)

    label_text = 'Profundidad [m]:'
    depth_list = [0, 100, 250, 500, 1000]
    default_depth = depth_list[0]
    depth_cb = self.__create_combobox_row(form_entries_frame, label_text, depth_list, default_depth)

    label_text = 'Título del gráfico:'
    chart_title_entry = self.__create_entry_row(form_entries_frame, label_text)

    label_text = 'Paleta de colores:'
    palette_colors_list = ['OrRd', 'plasma', 'plasma', 'Greens', 'viridis']
    palette_colors_cb = self.__create_combobox_row(form_entries_frame, label_text, palette_colors_list)

    # Following entries will be hidden or shown depending on the selected build method.

    self.__static_build_method_frame = ttk.Frame(form_entries_frame)
    self.__static_build_method_frame.pack_forget()
    label_text = 'Fecha objetivo:'
    target_date_entry = self.__create_date_entry_row(self.__static_build_method_frame, label_text)

    self.__animated_build_method_frame = ttk.Frame(form_entries_frame)
    self.__animated_build_method_frame.pack_forget()
    label_text = 'Unidad de duración:'
    duration_unit_list = ['Frames por segundo', 'Segundos por frame']
    duration_cb = self.__create_combobox_row(self.__animated_build_method_frame, label_text, duration_unit_list)
    label_text = 'Duración'
    duration_entry = self.__create_entry_row(self.__animated_build_method_frame, label_text)

    # Apply button.
    connect_button = ttk.Button(
      form_frame, 
      text='Aplicar', 
      command=lambda: self.__generate_chart(
        datasets_cb.get(), build_method_cb.get(),
        variable_cb.get(), depth_cb.get(),
        chart_title_entry.get(), palette_colors_cb.get(),
        target_date=target_date_entry.entry.get(),
        duration_unit=duration_cb.get(),
        duration=duration_entry.get()
      )
    )
    connect_button.pack(pady=10)

    # TODO: Display image in scroll_frame (hide by default?).
    # TODO: Display info about dataset in scroll_frame (hide by default).

  def __create_combobox_row(self, master, label_text, options, default_option=None):
    row_frame = ttk.Frame(master, bootstyle='default')
    row_frame.pack(fill='x', pady=5)

    label_frame = ttk.Frame(row_frame)
    label_frame.pack(fill='x', side='left')
    title_label = ttk.Label(label_frame, text=label_text, width=30)
    title_label.pack(fill='x')

    combobox_frame = ttk.Frame(row_frame)
    combobox_frame.pack(fill='x', side='right', expand=1)
    combobox = ttk.Combobox(combobox_frame, values=options, state='readonly')
    if default_option != None:
      combobox.set(default_option)
    combobox.pack(fill='x')

    return combobox

  def __create_entry_row(self, master, label_text):
    row_frame = ttk.Frame(master, bootstyle='default')
    row_frame.pack(fill='x', pady=5)

    label_frame = ttk.Frame(row_frame)
    label_frame.pack(fill='x', side='left')
    title_label = ttk.Label(label_frame, text=label_text, width=30)
    title_label.pack(fill='x')

    entry_frame = ttk.Frame(row_frame)
    entry_frame.pack(fill='x', side='right', expand=1)
    entry = ttk.Entry(entry_frame)
    entry.pack(fill='x')

    return entry

  def __create_date_entry_row(self, master, label_text):
    row_frame = ttk.Frame(master, bootstyle='default')
    row_frame.pack(fill='x', pady=5)

    label_frame = ttk.Frame(row_frame)
    label_frame.pack(fill='x', side='left')
    title_label = ttk.Label(label_frame, text=label_text, width=30)
    title_label.pack(fill='x')

    date_entry_frame = ttk.Frame(row_frame)
    date_entry_frame.pack(side='left')
    date_entry = ttk.DateEntry(date_entry_frame)
    date_entry.pack()

    tooltip_label = ttk.Label(row_frame, text='Info')
    tooltip_label.pack(side='left', padx=10)
    text_info = 'Clic izquierdo en la flecha para mover el calendario un mes.\n'
    text_info += 'Clic derecho en la flecha para mover el calendario un año.\n'
    text_info += 'Clic izquierdo en el título para restablecer el calendario a la fecha actual.'
    ToolTip(tooltip_label, text=text_info, bootstyle='info-inverse')

    return date_entry

  def __generate_chart(
    self, 
    datasets, 
    build_method, 
    variable, 
    depth, 
    chart_title, 
    palette_colors,
    target_date=None,
    duration_unit=None,
    duration=None
  ):
    print('-----------------------------')
    print(f'datasets: "{datasets}"')
    print(f'build_method: "{build_method}"')
    print(f'variable: "{variable}"')
    print(f'depth: "{depth}"')
    print(f'chart_title: "{chart_title}"')
    print(f'palette_colors: "{palette_colors}"')
    print(f'target_date: "{target_date}"')
    print(f'duration_unit: "{duration_unit}"')
    print(f'duration: "{duration}"')
    valid_fields = self.__fields_validation(datasets, build_method, variable, depth, chart_title, 
      palette_colors, target_date, duration_unit, duration)
    if valid_fields:
      # TODO: Continue with the chart generation.
      pass
  
  def __fields_validation(
    self, 
    datasets, 
    build_method, 
    variable, 
    depth, 
    chart_title, 
    palette_colors,
    target_date=None,
    duration_unit=None,
    duration=None
  ):
    chart_title = chart_title.strip()
    
    empty_fields = []
    if datasets == '': empty_fields.append('Dataset')
    if build_method == '': empty_fields.append('Método de construcción')
    if variable == '': empty_fields.append('Variable')
    if depth == '': empty_fields.append('Profundidad')
    if chart_title == '': empty_fields.append('Título del gráfico')
    if palette_colors == '': empty_fields.append('Paleta de colores')

    if self.__build_method == 'static':
      if target_date == '' or target_date == None:
        empty_fields.append('Fecha de objetivo')
    elif self.__build_method == 'animated':
      if duration_unit == '' or duration_unit == None:
        empty_fields.append('Unidad de duración')
      duration = duration.strip()
      if duration == '' or duration == None:
        empty_fields.append('Duración')
      else:
        try:
          duration = int(duration)
          if duration <= 0:
            raise Exception
        except:
          tk.messagebox.showerror(title='Error', message='La duración debe ser un número entero positivo.')
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
