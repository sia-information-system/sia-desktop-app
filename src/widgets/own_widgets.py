import ttkbootstrap as ttk

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