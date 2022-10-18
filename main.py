import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from PIL import ImageTk, Image

def sign_in_data_source(data_source, username, password, accept_terms):
    print("data_source:", data_source)
    print("username:", username)
    print("password:", password)
    print("accept_terms:", accept_terms)

    # Validate data.
    if data_source == "" or username == "" or password == "":
        tk.messagebox.showerror(title="Error", message="Todos los campos son obligatorios.")
        return
    if data_source not in DATA_SOURCES:
        tk.messagebox.showerror(title="Error", message="Fuente de datos no válida.\n" 
            "Por favor seleccione una de las fuentes de datos disponibles.")
        return
    if accept_terms == False:
        tk.messagebox.showerror(title="Error", message="Debe aceptar los términos y condiciones.")
        return

    # TODO: Sign in to data source.
    tk.messagebox.showinfo(title="Información", message="Conexión exitosa.")

def load_download_data_frame():
    clear_frames()
    download_data_frame.pack(fill="both", expand=1)

    form_frame = ttk.Frame(download_data_frame)
    form_frame.pack(pady=50)

    data_source_label = ttk.Label(form_frame, text="Selecciona la fuente de datos.")
    data_source_label.pack(fill="both", expand=1, pady=(10, 0))
    data_source_entry = ttk.Combobox(form_frame, values=DATA_SOURCES, state="readonly")
    data_source_entry.pack(fill="both", expand=1, pady=(10, 0))

    username_label = ttk.Label(form_frame, text="Nombre de usuario:")
    username_label.pack(fill="both", expand=1, pady=(10, 0))
    username_entry = ttk.Entry(form_frame)
    username_entry.pack(fill="both", expand=1, pady=(10, 0))

    password_label = ttk.Label(form_frame, text="Contraseña:")
    password_label.pack(fill="both", expand=1, pady=(10, 0))
    password_entry = ttk.Entry(form_frame, show="*")
    password_entry.pack(fill="both", expand=1, pady=(10, 0))

    global terms_status_var # Required variable as global. Local variable does not work.
    terms_status_var = tk.BooleanVar()
    terms_status_var.set(False)
    terms_check = ttk.Checkbutton(form_frame, text="Acepto los términos y condiciones", 
        variable=terms_status_var)
    terms_check.pack(fill="both", expand=1, pady=(10, 0))

    connect_button = ttk.Button(
        form_frame, 
        text="Conectar", 
        command=lambda: sign_in_data_source(
            data_source_entry.get(), username_entry.get(), 
            password_entry.get(), terms_status_var.get()
        )
    )
    connect_button.pack(pady=(10, 0))

def load_visualizations_frame():
    clear_frames()
    visualizations_frame.pack(fill="both", expand=1)
    label = ttk.Label(visualizations_frame, text="Herramienta para visualizar datos")
    label.pack(pady=(50, 0))

def load_downloaded_data_frame():
    clear_frames()
    downloaded_data_frame.pack(fill="both", expand=1)
    label = ttk.Label(downloaded_data_frame, text="Datos descargados")
    label.pack(pady=60)

def load_saved_charts_frame():
    clear_frames()
    saved_charts_frame.pack(fill="both", expand=1)
    label = ttk.Label(saved_charts_frame, text="Herramienta para visualizar datos")
    label.pack(pady=80)

def clear_frame(frame):
    # Destroy all widgets from frame, including inner frames.
    for widget in frame.winfo_children():
        widget.destroy()
    
    # Clear frame (do not destroy the frame itself, just hide it).
    frame.pack_forget()

# Clear all main frames that works as "window" for each option in the menu bar.
def clear_frames():
    # TODO: Search how to get all the frames inserted in the root to for loop them
    clear_frame(home_frame)
    clear_frame(download_data_frame)
    clear_frame(visualizations_frame)
    clear_frame(downloaded_data_frame)
    clear_frame(saved_charts_frame)

#  ------------------ Main ------------------

DATA_SOURCES = ["Copernicus", "NOAA"]

root = ttk.Window(themename="cosmo")
root.title("Caribbean Sea Data Repository")
root.geometry("600x400")

# Home frame.
home_frame = ttk.Frame(root)
home_frame.pack(fill="both", expand=1)
logo_img = ImageTk.PhotoImage(Image.open("images/unicaribe_logo.png"))
logo_label = ttk.Label(home_frame, image = logo_img)
logo_label.pack(pady=(80, 0))
name_app_label = ttk.Label(home_frame, text="Caribbean Sea Data Repository", font=("Helvetica", 16))
name_app_label.pack(pady=20)

# Create main frames ("windows") for each option in the menu bar.
download_data_frame = ttk.Frame(root)
visualizations_frame = ttk.Frame(root)
downloaded_data_frame = ttk.Frame(root)
saved_charts_frame = ttk.Frame(root)

# Menu bar.
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create "Archivo" menu option.
file_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Archivo", menu=file_menu)
file_menu.add_command(label="Nuevo", command=lambda: print("Nuevo archivo"))
file_menu.add_separator()
file_menu.add_command(label="Salir", command=root.quit)

# Create "Herramientas" menu option.
tools_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Herramientas", menu=tools_menu)
tools_menu.add_command(label="Descargar Datos", command=load_download_data_frame)
tools_menu.add_command(label="Visualizaciones", command=load_visualizations_frame)

# Create "Historial" menu option.
history_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Historial", menu=history_menu)
history_menu.add_command(label="Datos descargados", command=load_downloaded_data_frame)
history_menu.add_command(label="Visualizaciones guardadas", command=load_saved_charts_frame)

root.mainloop()