import json
import pathlib
import os
from utils.global_constants import HOME_PROJECTS_DIR, TMP_DIR
import xarray as xr

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
    'fromProjectPath': f'dataset/{project_dataset_filename}' if user_chose_select_data else None
  }
  metadata['worksheets'] = []

  # Save metadata json in project directory.
  json_filename = f'{project_name}.json'
  json_path = pathlib.Path(project_dir, json_filename)
  with open(json_path, 'w') as json_file: 
    json.dump(metadata, json_file, indent=2)

  return project_dir

def get_projects():
  return os.listdir(HOME_PROJECTS_DIR)

def project_exists(project_name):
  project = project_name.strip().lower()
  return project in get_projects()

# Return dataset using path in project.json
def get_dataset_project(project_path):
  # Find the project metadata (json file).
  json_file_path = None
  for filename in os.listdir(project_path):
    if filename.endswith('.json'):
      json_file_path = pathlib.Path(project_path, filename)
      break

  ds = None
  with open(json_file_path) as json_file:
    metadata = json.load(json_file)
    print(f'Project metadata: {metadata}')
    
    project_dataset_path = metadata['dataset']['fromProjectPath']
    dataset_path = pathlib.Path(project_path, project_dataset_path)
    ds = xr.open_dataset(dataset_path, engine='netcdf4')
    ds.close()
  return ds

def get_project_name(project_path):
  if not project_path:
    return ''

  # Find the project metadata (json file).
  json_file_path = None
  for filename in os.listdir(project_path):
    if filename.endswith('.json'):
      json_file_path = pathlib.Path(project_path, filename)
      break

  with open(json_file_path) as json_file:
    metadata = json.load(json_file)
    return metadata['project']['name']

# -------------------------------- Related to sheets ---------------------------------

def get_worksheets(project_path):
  # Find the project metadata (json file).
  json_file_path = None
  for filename in os.listdir(project_path):
    if filename.endswith('.json'):
      json_file_path = pathlib.Path(project_path, filename)
      break

  with open(json_file_path) as json_file:
    metadata = json.load(json_file)
    return metadata['worksheets']

def worksheet_exists(project_path, sheet_name):
  worksheets = get_worksheets(project_path)
  sheet_name = sheet_name.strip().lower()
  return sheet_name in [sheet['name'] for sheet in worksheets]

def add_worksheet(project_path, sheet_name, sheet_chart):
  # Find the project metadata (json file).
  json_file_path = None
  for filename in os.listdir(project_path):
    if filename.endswith('.json'):
      json_file_path = pathlib.Path(project_path, filename)
      break

  with open(json_file_path) as json_file:
    metadata = json.load(json_file)

  # Add new sheet to worksheets list.
  sheet_data = {
    'name': sheet_name.strip().lower(),
    'chart': sheet_chart,
    'parameters': {}
  }
  metadata['worksheets'].append(sheet_data)

  # Save updated metadata json in project directory.
  with open(json_file_path, 'w') as json_file:
    json.dump(metadata, json_file, indent=2)

def delete_worksheet(project_path, sheet_name):
  # Find the project metadata (json file).
  json_file_path = None
  for filename in os.listdir(project_path):
    if filename.endswith('.json'):
      json_file_path = pathlib.Path(project_path, filename)
      break

  with open(json_file_path) as json_file:
    metadata = json.load(json_file)

  # Find and remove the sheet with the provided name from the worksheets list.
  for sheet in metadata['worksheets']:
    if sheet['name'] == sheet_name.strip().lower():
      metadata['worksheets'].remove(sheet)
      break

  # Save updated metadata json in project directory.
  with open(json_file_path, 'w') as json_file:
    json.dump(metadata, json_file, indent=2)