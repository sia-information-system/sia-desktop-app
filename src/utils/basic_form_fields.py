import ttkbootstrap as ttk
from widgets.own_widgets import VerticalCollapsingFrame

def create_combobox_row(
  master, 
  label_text, 
  options, 
  default_option=None, 
  readonly=True,
  label_width=25,
  entry_width=None,
  tooltip_text=None
):
  row_frame = ttk.Frame(master, bootstyle='default')
  row_frame.pack(fill='x', pady=5)

  label_frame = ttk.Frame(row_frame)
  label_frame.pack(fill='x', side='left')
  title_label = ttk.Label(label_frame, text=label_text, width=label_width)
  title_label.pack(fill='x')

  combobox_frame = ttk.Frame(row_frame)
  combobox_frame.pack(fill='x', side='right', expand=1)
  state = 'readonly' if readonly else 'normal'
  combobox = ttk.Combobox(combobox_frame, values=options, state=state, width=entry_width)
  if default_option != None:
    combobox.set(default_option)

  # If user do not want to add a tooltip, then the combobox is packed directly.
  if not tooltip_text:
    combobox.pack(fill='x')
  else:
    combobox.pack(fill='x', side='left', expand=1)

    tooltip_label = ttk.Label(combobox_frame, text='Info')
    tooltip_label.pack(side='right', padx=10)
    ttk.tooltip.ToolTip(tooltip_label, text=tooltip_text, bootstyle='info-inverse')

  return combobox

def create_entry_row(
  master, 
  label_text,
  label_width=25,
  entry_width=None,
  show=None
):
  row_frame = ttk.Frame(master, bootstyle='default')
  row_frame.pack(fill='x', pady=5)

  label_frame = ttk.Frame(row_frame)
  label_frame.pack(fill='x', side='left')
  title_label = ttk.Label(label_frame, text=label_text, width=label_width)
  title_label.pack(fill='x')

  entry_frame = ttk.Frame(row_frame)
  entry_frame.pack(fill='x', side='right', expand=1)
  entry = ttk.Entry(entry_frame, width=entry_width, show=show)
  entry.pack(fill='x')

  return entry

def create_date_entry_row(master, label_text, label_width=25):
  row_frame = ttk.Frame(master, bootstyle='default')
  row_frame.pack(fill='x', pady=5)

  label_frame = ttk.Frame(row_frame)
  label_frame.pack(fill='x', side='left')
  title_label = ttk.Label(label_frame, text=label_text, width=label_width)
  title_label.pack(fill='x')

  date_entry_frame = ttk.Frame(row_frame)
  date_entry_frame.pack(fill='x', side='right', expand=1)
  date_entry = ttk.DateEntry(date_entry_frame, dateformat='%Y-%m-%d')
  date_entry.pack(fill='x', side='left', expand=1)

  tooltip_label = ttk.Label(date_entry_frame, text='Info')
  tooltip_label.pack(side='right', padx=10)
  text_info = 'Clic izquierdo en la flecha para mover el calendario un mes.\n'
  text_info += 'Clic derecho en la flecha para mover el calendario un año.'
  ttk.tooltip.ToolTip(tooltip_label, text=text_info, bootstyle='info-inverse')

  return date_entry

class MultipleCombobox():
  def __init__(
    self,
    master, 
    label_text, 
    options, 
    default_option=None, 
    readonly=True,
    label_width=25,
  ):
    self.combobox_list = []
    self.group_frame = None

    row_frame = ttk.Frame(master)
    row_frame.pack(fill='x', pady=5)

    label_frame = ttk.Frame(row_frame)
    label_frame.pack(fill='x', side='left')
    title_label = ttk.Label(label_frame, text=label_text, width=label_width)
    title_label.pack(fill='x')

    collaps_frame = VerticalCollapsingFrame(row_frame)
    collaps_frame.pack(fill='x', side='right', expand=1)
    self.group_frame = ttk.Frame(collaps_frame)
    collaps_frame.add(child=self.group_frame, title='Desplegar/Ocultar')

    create_cb_btn = ttk.Button(
      self.group_frame, 
      text='Añadir profundidad', 
      command=lambda : self.add_cb(
        options,
        default_option=default_option, 
        readonly=readonly
      ),
      bootstyle='dark'
    )
    create_cb_btn.pack(fill='x', padx=(20, 0), pady=(5, 0))
    
  def get(self):
    return [depth_cb.get() for depth_cb in self.combobox_list]

  def add_cb(self, options, default_option=None, readonly=True):
    combobox = self.__create_combobox(self.group_frame, options, default_option=default_option, readonly=readonly)
    self.combobox_list.append(combobox)

  def __create_combobox(self, master, options, default_option=None, readonly=True):
    frame = ttk.Frame(master)
    frame.pack(fill='x', padx=(20, 0), pady=(5, 0))

    state = 'readonly' if readonly else 'normal'
    combobox = ttk.Combobox(frame, values=options, state=state)
    if default_option != None:
      combobox.set(default_option)
    combobox.pack(side='left', fill='x', expand=1, padx=(0, 20))

    delete_btn = ttk.Button(
      frame, 
      text='Eliminar', 
      command=lambda : self.__delete_cb(frame), 
      bootstyle='danger'
    )
    delete_btn.pack(side='left')

    return combobox

  def __delete_cb(self, frame):
    frame_name = frame.winfo_name()
    for combobox in self.combobox_list:
      cb_parent_name = combobox.winfo_parent().split('.')[-1]
      if cb_parent_name == frame_name:
        combobox.destroy()
        self.combobox_list.remove(combobox)
        break
    frame.destroy()