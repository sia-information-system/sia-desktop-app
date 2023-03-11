import json
import zipfile
import pathlib
import os
from utils.global_constants import HOME_PROJECTS_DIR, TMP_DIR
import xarray as xr

PROJECT_EXTENSION = '.zip'

def save_project(project_name, dataset_path=None):
  user_chose_select_data = dataset_path != None

  # Make a copy of original dataset in HOME_DATASETS_DIR to HOME_PROJECTS_DIR/<Project>/dataset
  project_dataset_dir_path = None
  project_dataset_path = None
  project_dataset_filename = None
  
  if user_chose_select_data:
    project_dataset_dir_path = pathlib.Path(HOME_PROJECTS_DIR, 'dataset')
    project_dataset_dir_path.mkdir()
    project_dataset_filename = 'data' + pathlib.Path(dataset_path).suffix
    project_dataset_path = pathlib.Path(project_dataset_dir_path, project_dataset_filename)
    with open(dataset_path, 'rb') as dataset_file:
      with open(project_dataset_path, 'wb') as project_dataset_file:
        project_dataset_file.write(dataset_file.read())

  # Project description that will be saved as json file.
  project_name = project_name.strip().lower()
  data = {}
  data['project'] = { 'name': project_name }
  data['dataset'] = { 
    'originalPath': dataset_path,
    'fromProjectPath': f'dataset/{project_dataset_filename}' if user_chose_select_data else None
  }
  data['worksheets'] = {}


  # Create zip file.
  zip_filename = project_name + PROJECT_EXTENSION
  zip_path = pathlib.Path(HOME_PROJECTS_DIR, zip_filename)

  with zipfile.ZipFile(zip_path, 'w') as zipf:
    json_data = json.dumps(data, indent=2).encode('utf-8')
    json_filename = f'{project_name}.json'
    zipf.writestr(json_filename, json_data)
    # Include dataset in zip file.
    if user_chose_select_data:
      zipf.write(project_dataset_path, arcname=f'dataset/{project_dataset_filename}')

  # Remove dataset and dataset dir.
  if user_chose_select_data:
    os.remove(project_dataset_path)
    os.rmdir(project_dataset_dir_path)

  return zip_path

def get_projects():
  projects = []
  for project in os.listdir(HOME_PROJECTS_DIR):
    if project.endswith(PROJECT_EXTENSION):
      projects.append(project)
  return projects

def project_exists(project_name):
  project_name = project_name.strip().lower()
  project = project_name + PROJECT_EXTENSION
  return project in get_projects()

# Return dataset using path in project.json
def get_dataset_project(project_path):
  ds = None

  with zipfile.ZipFile(project_path, 'r') as zipf:
    # Find the only json file (project metadat) in the zip file.
    json_filename = None
    for filename in zipf.namelist():
      if filename.endswith('.json'):
        json_filename = filename
        break
    with zipf.open(json_filename) as json_file:
      metadata = json.load(json_file)
      print(f'Project metadata: {metadata}')
      
      dataset_zip_path = metadata['dataset']['fromProjectPath']
      zipf.extract(dataset_zip_path, TMP_DIR)
      extracted_dataset_path = pathlib.Path(TMP_DIR, dataset_zip_path)
      ds = xr.open_dataset(extracted_dataset_path, engine='netcdf4')
      ds.close()
  
      # Delete temporary files.
      os.remove(extracted_dataset_path)
      os.rmdir(pathlib.Path(TMP_DIR, 'dataset'))

  return ds