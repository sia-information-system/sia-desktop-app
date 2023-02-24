import os
import pathlib
import sys
import traceback
from configparser import ConfigParser

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

def get_directory_from_config(config_var):
  # Initial segments move to root directory.
  path_segments = [pathlib.Path(__file__).parent.absolute(), '..', '..']
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
