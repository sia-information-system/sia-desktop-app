import ttkbootstrap as ttk
from views.templates.scrollable_view import ScrollableView

class UserManualView(ScrollableView):
  def __init__(self, master):
    super().__init__(master)

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    title_view_label = ttk.Label(self.scroll_frame, text='Manual de usuario', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=10)
