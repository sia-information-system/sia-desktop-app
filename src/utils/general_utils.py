import os
import pathlib
import math
import sys
import ttkbootstrap as ttk
from configparser import ConfigParser
import utils.global_variables as global_vars

def read_config():
  config_path = pathlib.Path(
    pathlib.Path(__file__).parent.absolute(),
    '..',
    '..',
    'etc',
    'config.ini')
  config = ConfigParser()
  config.read(config_path)
  return config

def mkdir_r(path):
  os.makedirs(path, exist_ok=True)

def get_directory_from_config(config_var, start_from='root'):
  path_segments = []
  # Initial segments 
  if start_from == 'root':
    path_segments.extend([pathlib.Path(__file__).parent.absolute(), '..', '..'])
  elif start_from == 'user_home':
    home_dirname='SIA'
    path_segments.extend([pathlib.Path.home(), home_dirname])

  try:
    config = read_config()
    user_path = config['DEFAULT'][config_var]
    user_path_segments = [segment for segment in user_path.split('/') if segment != '']
    if len(user_path_segments) == 0:
      raise Exception()
    for directory in user_path_segments:
      path_segments.append(directory)
    directory_path = pathlib.Path(*path_segments)
    mkdir_r(directory_path)
    return directory_path
  except:
    print('Something went wrong while trying to get the directory from config.', file=sys.stderr)
    print(f'The config.ini there not exists or the variable {config_var} is not defined.', file=sys.stderr)
    sys.exit(1)

def find_view(root_window, view_class):
  '''
  view_class: String class of the view to find.
  '''
  # Format used in tkinter to represent a class who inherits from ttk.Frame
  format_view_class = '.!' + view_class.lower()
  for view in root_window.winfo_children():
    if format_view_class == str(view):
      return view
  return None

def change_view(root_window, view):
  clear_views(root_window)
  view.load_view()

# Clear all main views (frames) that works as 'window' for each option in the menu bar.
def clear_views(root_window):
  # print('--------------------')
  # print(f'root_window: {root_window}. type: {type(root_window)}')
  for view in root_window.winfo_children():
    if isinstance(view, ttk.Frame):
      clear_view(view)

def clear_view(view):
  # print(f'view: {view}. type: {type(view)}')
  # Destroy all widgets from view (frame), including inner widgets.
  for widget in view.winfo_children():
    # print(f'\twidget: {widget}. type: {type(widget)}')
    widget.destroy()

  # Clear view, do not destroy the view (frame) itself just hide it.
  view.pack_forget()

def round_ceil(number, decimals=0):
  multiplier = 10 ** decimals
  return math.ceil(number * multiplier) / multiplier

def round_floor(number, decimals=0):
  multiplier = 10 ** decimals
  return math.floor(number * multiplier) / multiplier

def is_project_loaded():
  return global_vars.current_project_path and global_vars.current_project_dataset

def is_project_configured():
  return (global_vars.time_dim and global_vars.depth_dim and \
    global_vars.lon_dim and global_vars.lat_dim and \
    global_vars.northward_var and global_vars.eastward_var)