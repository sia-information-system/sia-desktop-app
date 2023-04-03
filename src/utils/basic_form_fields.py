import ttkbootstrap as ttk

def create_combobox_row(
  master, 
  label_text, 
  options, 
  default_option=None, 
  readonly=True,
  label_width=25,
  entry_width=None
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
  combobox.pack(fill='x')

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
  date_entry_frame.pack(side='left')
  date_entry = ttk.DateEntry(date_entry_frame, dateformat='%Y-%m-%d')
  date_entry.pack()

  tooltip_label = ttk.Label(row_frame, text='Info')
  tooltip_label.pack(side='left', padx=10)
  text_info = 'Clic izquierdo en la flecha para mover el calendario un mes.\n'
  text_info += 'Clic derecho en la flecha para mover el calendario un año.'
  ttk.tooltip.ToolTip(tooltip_label, text=text_info, bootstyle='info-inverse')

  return date_entry