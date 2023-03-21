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
  data = {}
  data['project'] = { 'name': project_name }
  data['dataset'] = { 
    'originalPath': dataset_path,
    'fromProjectPath': f'dataset/{project_dataset_filename}' if user_chose_select_data else None
  }
  data['worksheets'] = []

  # Save data json in project directory.
  json_filename = f'{project_name}.json'
  json_path = pathlib.Path(project_dir, json_filename)
  with open(json_path, 'w') as json_file: 
    json.dump(data, json_file, indent=2)

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

def add_sheet(project_path, sheet_name, sheet_chart):
  metadata= None

  with zipfile.ZipFile(project_path, 'r') as zipf:
    # Find the only json file (project metadat) in the zip file.
    json_filename = None
    for filename in zipf.namelist():
      if filename.endswith('.json'):
        json_filename = filename
        break

    print(f'json_filename: {json_filename}')

    # Add a new worsheet (object) which has 2 keys: name and chart
    with zipf.open(json_filename) as json_file:
      metadata = json.load(json_file)
      metadata['worksheets'].append({
        'name': sheet_name,
        'chart_type': sheet_chart,
        'parameters': {}
      })
      print(f'New metadata: {metadata}')

  # FIXME: Files are duplicated.
  with zipfile.ZipFile(project_path, 'a') as zipf:
    json_data = json.dumps(metadata, indent=2).encode('utf-8')
    zipf.writestr(json_filename, json_data)