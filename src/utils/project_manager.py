import json
import zipfile
import pathlib
import os
from utils.global_constants import PROJECTS_DIR
PROJECT_EXTENSION = '.zip'

def save_project(project_name, dataset_path=None):
  project_name = project_name.strip().lower()
  data = {}
  data['project'] = { 'name': project_name }
  data['dataset'] = { 'path': dataset_path }
  data['worksheets'] = {}

  zip_filename = project_name + PROJECT_EXTENSION
  zip_path = pathlib.Path(PROJECTS_DIR, zip_filename)

  with zipfile.ZipFile(zip_path, 'w') as zip_file:
    json_data = json.dumps(data, indent=2).encode('utf-8')
    json_filename = f'{project_name}.json'
    zip_file.writestr(json_filename, json_data)

  return zip_path

def get_projects():
  projects = []
  for project in os.listdir(PROJECTS_DIR):
    if project.endswith(PROJECT_EXTENSION):
      projects.append(project)
  return projects

def project_exists(project_name):
  project_name = project_name.strip().lower()
  project = project_name + PROJECT_EXTENSION
  return project in get_projects()
