import ttkbootstrap as ttk
import random

class AboutAppView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)

  def load_view(self):
    self.pack(fill='both', expand=1)

    title_view_label = ttk.Label(self, text='Sobre la aplicación', font=('TkDefaultFont', 14))
    title_view_label.pack(pady=(10, 0))

    content_frame = ttk.Frame(self, bootstyle='default')
    content_frame.pack(fill='x', padx=10, pady=10)

    text = ttk.Text(content_frame, wrap='word')
    text.pack(fill='both', expand=1)

    developers = [
      {'name': 'Alexis Montejo', 'email': '180300337@ucaribe.edu.mx'},
      {'name': 'Jasson Perez', 'email': '180300346@ucaribe.edu.mx'},
      {'name': 'Julian Maldonado', 'email': '180300376@ucaribe.edu.mx'}
    ]
    random.shuffle(developers)

    text_info = 'Esta aplicación fue desarrollada como parte del proyecto terminal titulado ' \
      '"Sistema de información para el análisis de datos oceanográficos del Caribe mexicano". ' \
      'Con el fin de facilitar la descarga y visualización de datos oceanográficos, dirigido a ' \
      'estudiantes y profesores de la carrera de Ingeniería Ambiental de la Universidad del Caribe.' \
      '\n\n' \
      'La aplicación fue desarrollada por los siguientes estudiantes de la Universidad del Caribe ' \
      'de la carrera de Ingeniería en Datos e Inteligencia Organizacional:' \
      '\n\n' \

    for developer in developers:
      text_info += f'- {developer["name"]}\t\t\tEmail: {developer["email"]}' \
      '\n' \

    text_info += '\n' \
      'Bajo el asesoramiento del Dr. Fernando Gómez.' \
      '\n\n' \
      'Version: 1.0.0' \
      '\n' \
      'Fecha de lanzamiento: 10/05/2023' \
      '\n' \

    text.insert('end', text_info)
    text.configure(state='disabled')
