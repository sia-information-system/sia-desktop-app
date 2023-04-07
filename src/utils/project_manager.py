import json
import pathlib
import os
import xarray as xr
import utils.general_utils as gen_utils
import utils.global_variables as global_vars
from utils.global_constants import HOME_PROJECTS_DIR, PROJECT_EXTENSION
from tkinter.filedialog import askopenfilename

def get_project_metadata_file_path(project_path):
  for filename in os.listdir(project_path):
    if filename.endswith(PROJECT_EXTENSION):
      return pathlib.Path(project_path, filename)

# ---------------------------------------------------------------------------------

def open_project(root_window):
  project_metadata_file_path = askopenfilename(
    title='Selecciona el proyecto',
    initialdir=HOME_PROJECTS_DIR,
    filetypes=[('sia files', f'*{PROJECT_EXTENSION}')]
  )
  if not project_metadata_file_path:
    return
  project_path = pathlib.Path(project_metadata_file_path).parent.absolute()
  global_vars.current_project_path = project_path
  global_vars.current_project_dataset = get_dataset_project(project_path)

  workspace_view = gen_utils.find_view(root_window, 'WorkspaceView')
  gen_utils.change_view(root_window, workspace_view)

def save_project(project_name, dataset_path=None):
  user_chose_select_data = dataset_path != None

  # Create project directory.
  project_name = project_name.strip().lower()
  project_dir = pathlib.Path(HOME_PROJECTS_DIR, project_name)
  project_dir.mkdir()

  # Make a copy of original dataset in HOME_DATASETS_DIR to HOME_PROJECTS_DIR/<Project>/dataset
  project_dataset_filename = None
  
  if user_chose_select_data:
    project_dataset_dir_path = pathlib.Path(project_dir, 'dataset')
    project_dataset_dir_path.mkdir()
    project_dataset_filename = 'data' + pathlib.Path(dataset_path).suffix
    project_dataset_path = pathlib.Path(project_dataset_dir_path, project_dataset_filename)
    with open(dataset_path, 'rb') as dataset_file:
      with open(project_dataset_path, 'wb') as project_dataset_file:
        project_dataset_file.write(dataset_file.read())

  # Project description that will be saved as json file.
  metadata = {}
  metadata['project'] = { 'name': project_name }
  metadata['dataset'] = { 
    'originalPath': dataset_path,
    'fromProjectPath': f'dataset/{project_dataset_filename}' if user_chose_select_data else None,
    'config': {
      'dimensions': {
        'time': None,
        'depth': None,
        'lon': None,
        'lat': None
      },
      'variables': {
        'northward': None,
        'eastward': None
      }
    }
  }
  metadata['worksheets'] = []

  # Save metadata json in project directory.
  json_filename = f'{project_name}{PROJECT_EXTENSION}'
  json_path = pathlib.Path(project_dir, json_filename)
  with open(json_path, 'w') as json_file: 
    json.dump(metadata, json_file, indent=2)

  return project_dir

def get_projects():
  return os.listdir(HOME_PROJECTS_DIR)

def project_exists(project_name):
  project = project_name.strip().lower()
  return project in get_projects()

def get_project_name(project_path):
  if not project_path:
    return ''

  # Find the project metadata (json file).
  project_metadata_path = get_project_metadata_file_path(project_path)
  with open(project_metadata_path) as json_file:
    metadata = json.load(json_file)
    return metadata['project']['name']

# --------------------------------  Related project dataset --------------------------------

# Return dataset using path in project.json
def get_dataset_project(project_path):
  # Find the project metadata (json file).
  project_metadata_path = get_project_metadata_file_path(project_path)
  ds = None
  with open(project_metadata_path) as json_file:
    metadata = json.load(json_file)
    project_dataset_path = metadata['dataset']['fromProjectPath']
    dataset_path = pathlib.Path(project_path, project_dataset_path)
    ds = xr.open_dataset(dataset_path, engine='netcdf4')
    ds.close()
  return ds

def save_dataset_config(
  project_path,
  time_dim,
  depth_dim,
  lon_dim,
  lat_dim,
  northward_var,
  eastward_var
):
  # Find the project metadata (json file).
  project_metadata_path = get_project_metadata_file_path(project_path)
  with open(project_metadata_path) as json_file:
    metadata = json.load(json_file)

  # Update dataset config.
  metadata['dataset']['config']['dimensions']['time'] = time_dim
  metadata['dataset']['config']['dimensions']['depth'] = depth_dim
  metadata['dataset']['config']['dimensions']['lon'] = lon_dim
  metadata['dataset']['config']['dimensions']['lat'] = lat_dim
  metadata['dataset']['config']['variables']['northward'] = northward_var
  metadata['dataset']['config']['variables']['eastward'] = eastward_var

  # Save updated metadata json in project directory.
  with open(project_metadata_path, 'w') as json_file:
    json.dump(metadata, json_file, indent=2)

def get_dataset_config(project_path):
  # Find the project metadata (json file).
  project_metadata_path = get_project_metadata_file_path(project_path)
  with open(project_metadata_path) as json_file:
    metadata = json.load(json_file)
    return metadata['dataset']['config']

# -------------------------------- Related to sheets ---------------------------------

def get_worksheets(project_path):
  # Find the project metadata (json file).
  project_metadata_path = get_project_metadata_file_path(project_path)
  with open(project_metadata_path) as json_file:
    metadata = json.load(json_file)
    return metadata['worksheets']

def worksheet_exists(project_path, sheet_name):
  worksheets = get_worksheets(project_path)
  sheet_name = sheet_name.strip().lower()
  return sheet_name in [sheet['name'] for sheet in worksheets]

def add_worksheet(project_path, sheet_name, sheet_chart_type):
  # Find the project metadata (json file).
  project_metadata_path = get_project_metadata_file_path(project_path)
  with open(project_metadata_path) as json_file:
    metadata = json.load(json_file)

  # Add new sheet to worksheets list.
  sheet_data = {
    'name': sheet_name.strip().lower(),
    'chart_type': sheet_chart_type,
    'parameters': {}
  }
  metadata['worksheets'].append(sheet_data)

  # Save updated metadata json in project directory.
  with open(project_metadata_path, 'w') as json_file:
    json.dump(metadata, json_file, indent=2)

def delete_worksheet(project_path, sheet_name):
  # Find the project metadata (json file).
  project_metadata_path = get_project_metadata_file_path(project_path)
  with open(project_metadata_path) as json_file:
    metadata = json.load(json_file)

  # Find and remove the sheet with the provided name from the worksheets list.
  for sheet in metadata['worksheets']:
    if sheet['name'] == sheet_name.strip().lower():
      metadata['worksheets'].remove(sheet)
      break

  # Save updated metadata json in project directory.
  with open(project_metadata_path, 'w') as json_file:
    json.dump(metadata, json_file, indent=2)

# -------------------------------------- Configurations -------------------------------------------