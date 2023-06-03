import textwrap
import ttkbootstrap as ttk
from ttkbootstrap.dialogs.dialogs import QueryDialog, Messagebox
import sia_app.utils.global_variables as global_vars
import sia_app.utils.project_manager as prj_mgmt

# Docs for QueryDialog: https://ttkbootstrap.readthedocs.io/en/latest/api/dialogs/querydialog/
class NewSheetDialogBox(QueryDialog):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.chart_type_cb = None # Combobox widget for chart type.
    self.chart_type_cb_result = None # Value of the combobox widget.
    self.proceed_to_add = False
    self.chart_type_dict = {
      'Mapa de calor': 'HEATMAP',
      'Curva de nivel': 'CONTOUR_MAP',
      'Serie de tiempo': 'TIME_SERIES',
      'Gráfica de corrientes': 'CURRENTS_CHART',
      'Rosa de los vientos': 'WIND_ROSE',
      'Perfil vertical': 'VERTICAL_PROFILE',
      'Corte vertical': 'VERTICAL_SLICE',
    }

  def create_body(self, master):
    '''Override. Adds the form section.'''
    self.proceed_to_add = False

    form_frame = ttk.Frame(master, padding=self._padding)
    if self._prompt:
      for p in self._prompt.split('\n'):
        prompt = '\n'.join(textwrap.wrap(p, width=self._width))
        prompt_label = ttk.Label(form_frame, text=prompt)
        prompt_label.pack(pady=(0, 20), anchor='n')

    entry_label = ttk.Label(form_frame, text='Nombre de la hoja:')
    entry_label.pack(pady=(0, 5), fill='x', anchor='n')
    name_entry = ttk.Entry(master=form_frame)
    name_entry.insert('end', self._initialvalue)
    name_entry.pack(pady=(0, 10), fill='x')
    name_entry.bind('<Return>', self.on_submit)
    name_entry.bind('<KP_Enter>', self.on_submit)
    name_entry.bind('<Escape>', self.on_cancel)

    combobox_label = ttk.Label(form_frame, text='Tipo de visualización:')
    combobox_label.pack(pady=(0, 5), fill='x', anchor='n')
    chart_types = list(self.chart_type_dict.keys())
    chart_type_cb = ttk.Combobox(form_frame, values=chart_types, state='readonly')
    chart_type_cb.pack(fill='both', pady=(10, 0))
    chart_type_cb.pack(pady=(0, 10), fill='x')
    chart_type_cb.bind('<Return>', self.on_submit)
    chart_type_cb.bind('<KP_Enter>', self.on_submit)
    chart_type_cb.bind('<Escape>', self.on_cancel)

    form_frame.pack(fill='x', expand=1)
    self._initial_focus = name_entry
    self.chart_type_cb = chart_type_cb

  def on_submit(self, *_):
    '''Override. Save result, destroy the toplevel, and apply any post-hoc data manipulations.'''
    self._result = self._initial_focus.get() # Entry worksheet name.
    self.chart_type_cb_result = self.chart_type_cb.get()

    # Validate data.
    valid_result = self.validate()
    if not valid_result:
        return  # keep toplevel open for valid response

    self._toplevel.destroy()
    self.apply()
    self.proceed_to_add = True

  def validate(self):
    ''' overridde
    Validate the data
    This method is called automatically to validate the data before
    the dialog is destroyed. Can be subclassed and overridden.
    '''

    if self._result == '':
      Messagebox.ok(
        message='Asegurese de ingresar un nombre para la hoja',
        title='Datos faltantes',
        parent=self._toplevel
      )
      return False

    worksheet_exists = prj_mgmt.worksheet_exists(
      sheet_name=self._result, 
      project_path=global_vars.current_project_path
    )
    if worksheet_exists:
      Messagebox.ok(
        message='Ya existe una hoja con ese nombre, ingrese otro.',
        title='Datos duplicados',
        parent=self._toplevel
      )
      return False

    if self.chart_type_cb_result == '':
      Messagebox.ok(
        message='Asegurese de seleccionar un tipo de visualización',
        title='Datos faltantes',
        parent=self._toplevel
      )
      return False

    # Valid result
    return True

  def create_buttonbox(self, master):
    '''Overrides the parent method; adds the message buttonbox'''
    frame = ttk.Frame(master, padding=(5, 10))

    submit = ttk.Button(
      master=frame,
      bootstyle='primary',
      text='Crear',
      command=self.on_submit,
    )
    submit.pack(padx=5, side='right')
    submit.lower()  # set focus traversal left-to-right

    cancel = ttk.Button(
      master=frame,
      bootstyle='secondary',
      text='Cancelar',
      command=self.on_cancel,
    )
    cancel.pack(padx=5, side='right')
    cancel.lower()  # set focus traversal left-to-right

    ttk.Separator(self._toplevel).pack(fill='x')
    frame.pack(side='bottom', fill='x', anchor='s')

  def get_sheet_data(self):
    return {
      'proceed_to_add': self.proceed_to_add,
      'name': self._result, 
      'chart_type': self.chart_type_dict[self.chart_type_cb_result] if self.proceed_to_add else None
    }

# Base on Collapsing Frame of ttkbootstrap examples.
# https://ttkbootstrap.readthedocs.io/en/latest/gallery/collapsingframe/ 
class VerticalCollapsingFrame(ttk.Frame):
  '''A collapsible frame widget that opens and closes with a click.'''

  def __init__(self, master, **kwargs):
    super().__init__(master, **kwargs)
    self.columnconfigure(0, weight=1)
    self.cumulative_rows = 0

    self.btn = None
    # Icons
    self.icons = [
      '🔼',
      '🔽'
    ]

  def add(self, child, title='', bootstyle='primary', **kwargs):
    '''Add a child to the collapsible frame

    Parameters:

      child (Frame):
        The child frame to add to the widget.

      title (str):
        The title appearing on the collapsible section header.

      bootstyle (str):
        The style to apply to the collapsible section header.

      **kwargs (Dict):
        Other optional keyword arguments.
    '''
    if child.winfo_class() != 'TFrame':
      return

    style_color = ttk.style.Bootstyle.ttkstyle_widget_color(bootstyle)
    frm = ttk.Frame(self, bootstyle=style_color)
    frm.grid(row=self.cumulative_rows, column=0, sticky='ew')

    # header title
    header = ttk.Label(
      master=frm,
      text=title,
      bootstyle=(style_color, 'inverse')
    )
    if kwargs.get('textvariable'):
      header.configure(textvariable=kwargs.get('textvariable'))
    header.pack(side='left', fill='both', padx=10)

    # header toggle button
    def _func(c=child): return self._toggle_open_close(c)
    self.btn = ttk.Button(
      master=frm,
      text=self.icons[0],
      bootstyle=style_color,
      command=_func
    )
    self.btn.pack(side='right')

    # assign toggle button to child so that it can be toggled
    child.btn = self.btn
    child.grid(row=self.cumulative_rows + 1, column=0, sticky='nsew')

    # increment the row assignment
    self.cumulative_rows += 2

  def _toggle_open_close(self, child):
    '''Open or close the section and change the toggle button 
    image accordingly.

    Parameters:

      child (Frame):
        The child element to add or remove from grid manager.
    '''
    if child.winfo_viewable():
      child.grid_remove()
      child.btn.configure(text=self.icons[1])
    else:
      child.grid()
      child.btn.configure(text=self.icons[0])