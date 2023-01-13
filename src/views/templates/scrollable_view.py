import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame

class ScrollableView(ttk.Frame):
  def __init__(self, master):
    # TODO: Styles in FRAMES to visualize the containers, delete or modify them in production.
    super().__init__(master, bootstyle='default')
    self.scroll_frame = None

  def load_view(self):
    self.scroll_frame = ScrolledFrame(self, bootstyle='default')
    self.scroll_frame.pack(fill='both', expand=1)
