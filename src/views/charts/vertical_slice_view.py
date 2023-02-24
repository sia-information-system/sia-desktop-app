import ttkbootstrap as ttk
from views.templates.scrollable_view import ScrollableView

class VerticalSliceView(ScrollableView):
  def __init__(self, master):
    super().__init__(master)

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    # ------------------ Elements of the view  ------------------

    title_label = ttk.Label(self.scroll_frame, text='Vertical Slice visualization', font=('Helvetica', 14))
    title_label.pack(pady=10)

    # Random widgets to test scroll.
    for i in range(50):
      ttk.Label(self.scroll_frame, text=f'Label {str(i+1)} in VerticalSliceView.').pack(pady=5)
