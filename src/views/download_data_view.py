import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox

class DownloadDataView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)
    self.data_sources = ['Copernicus', 'NOAA']
    self.terms_status_var = tk.BooleanVar()

  def sign_in_data_source(self, data_source, username, password, accept_terms):
    # Validate data.
    if data_source == '' or username == '' or password == '':
      tk.messagebox.showerror(title='Error', message='Todos los campos son obligatorios.')
      return
    if data_source not in self.data_sources:
      tk.messagebox.showerror(title='Error', message='Fuente de datos no válida.\n' 
          'Por favor seleccione una de las fuentes de datos disponibles.')
      return
    if accept_terms == False:
      tk.messagebox.showerror(title='Error', message='Debe aceptar los términos y condiciones.')
      return

    # TODO: Sign in to data source.
    tk.messagebox.showinfo(title='Información', message='Conexión exitosa.')

  def load_view(self):
    self.pack(fill='both', expand=1)

    form_frame = ttk.Frame(self)
    form_frame.pack(pady=50)

    data_source_label = ttk.Label(form_frame, text='Selecciona la fuente de datos.')
    data_source_label.pack(fill='both', pady=(10, 0))
    data_source_cb = ttk.Combobox(form_frame, values=self.data_sources, state='readonly')
    data_source_cb.pack(fill='both', pady=(10, 0))

    username_label = ttk.Label(form_frame, text='Nombre de usuario:')
    username_label.pack(fill='both', pady=(10, 0))
    username_entry = ttk.Entry(form_frame)
    username_entry.pack(fill='both', pady=(10, 0))

    password_label = ttk.Label(form_frame, text='Contraseña:')
    password_label.pack(fill='both', pady=(10, 0))
    password_entry = ttk.Entry(form_frame, show='*')
    password_entry.pack(fill='both', pady=(10, 0))

    self.terms_status_var.set(False)
    terms_check = ttk.Checkbutton(form_frame, text='Acepto los términos y condiciones', 
      variable=self.terms_status_var)
    terms_check.pack(fill='both', pady=(10, 0))

    connect_button = ttk.Button(
      form_frame, 
      text='Conectar', 
      command=lambda: self.sign_in_data_source(
        data_source_cb.get(), username_entry.get(),
        password_entry.get(), self.terms_status_var.get()
      )
    )
    connect_button.pack(pady=(20, 0))
