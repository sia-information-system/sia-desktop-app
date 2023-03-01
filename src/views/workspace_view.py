import ttkbootstrap as ttk
import utils.global_variables as global_vars

class WorkspaceView(ttk.Frame):
  def __init__(self, master):
    super().__init__(master)

  def load_view(self):
    self.pack(fill='both', expand=1)
    label = ttk.Label(self, text='Espacio de trabajo')
    label.pack(pady=80)

    current_project_label = ttk.Label(self, text=f'Ruta de proyecto actual: {global_vars.current_project_path}')
    current_project_label.pack(pady=10)
    