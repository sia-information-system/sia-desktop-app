import ttkbootstrap as ttk

class ScrollableView(ttk.Frame):
  def __init__(self, master):
    # TODO: Styles in FRAMES to visualize the containers, delete or modify them in production.
    super().__init__(master, bootstyle='primary')
    self.scroll_frame = None

  def load_view(self):
    # Create a subframe to hold the canvas and the scrollbar. This allows destroy and recreate the canvas.
    subframe = ttk.Frame(self, bootstyle='secondary')
    subframe.pack(fill='both', expand=1)

    scrollbar = ttk.Scrollbar(subframe, bootstyle='secondary-round')
    scrollbar.pack(side='right', fill='y')
    scrollbar.set(0, 1)

    canvas = ttk.Canvas(
      master=subframe,
      relief='flat',
      borderwidth=0,
      selectborderwidth=0,
      highlightthickness=0,
      yscrollcommand=scrollbar.set,
      width=800
    )
    canvas.pack(fill='y', expand=1)

    # Adjust the scrollregion when the size of the canvas changes
    canvas.bind(
      sequence='<Configure>',
      func=lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
    )
    scrollbar.configure(command=canvas.yview)

    self.scroll_frame = ttk.Frame(canvas, bootstyle='dark')
    canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw', width=800)