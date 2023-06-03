import ttkbootstrap as ttk
import webbrowser
from sia_app.views.templates.scrollable_view import ScrollableView


class UserManualView(ScrollableView):
  def __init__(self, master):
    super().__init__(master)

  def load_view(self):
    self.pack(fill='both', expand=1)
    super().load_view()

    title_view_label = ttk.Label(self.scroll_frame, text='Manual de usuario', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=10)


class LinksToDocsView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)
    self.docs_website = 'https://sia-information-system.github.io/sia-website/'

  def load_view(self):
    self.pack(fill='both', expand=1)

    title_view_label = ttk.Label(self, text='Documentación y manual de usuario', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=(10, 0))

    content_frame = ttk.Frame(self, bootstyle='default')
    content_frame.pack(fill='x', padx=10, pady=10)

    text = ttk.Text(content_frame, wrap='word', height=10)
    text.pack(fill='both', expand=1)

    text_info = 'Para acceder a la documentación de esta aplicación, visite el siguiente sitio web. '
    text_info += 'En él encontrá recursos útiles como: manual de usuario, video tutoriales, '
    text_info += 'publicación de versiones, entre otros.\n\n'
    text_info += f'Link: {self.docs_website}\n'

    text.insert('end', text_info)
    text.configure(state='disabled')

    controls_frame = ttk.Frame(self, bootstyle='default')
    controls_frame.pack(fill='x', padx=10, pady=10)

    link_button = ttk.Button(
      controls_frame, 
      text='Abrir sitio web',
      state='enabled',
      command=lambda: webbrowser.open(self.docs_website)
    )
    link_button.pack()
