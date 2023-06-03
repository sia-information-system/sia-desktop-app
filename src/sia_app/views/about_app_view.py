import ttkbootstrap as ttk
import random
from importlib import metadata

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
      {'name': 'Alexis Montejo', 'email': 'https://www.linkedin.com/in/alemontejolp/'},
      {'name': 'Jasson Perez', 'email': 'https://www.linkedin.com/in/jasson-perez-bab0aa232/'},
      {'name': 'Julian Maldonado', 'email': 'https://www.linkedin.com/in/julianmaldonadoag/'}
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
      text_info += f'- {developer["name"]}\t\t\tLinkedIn: {developer["email"]}' \
      '\n' \

    text_info += '\n' \
      'Bajo el asesoramiento del Dr. Fernando Gómez.' \
      '\n\n' \
      'Para más formas de contacto, visita la sección "Contribuidores" de la página web del proyecto. ' \
      'Puedes acceder desde el menú "Documentación" de esta aplicación.' \
      '\n\n' \
      f'Version: {metadata.version("sia-app")}' \
      '\n' \
      'Fecha de la primera publicación (1.0.0): 2023/05/10' \
      '\n' \

    text.insert('end', text_info)
    text.configure(state='disabled')
