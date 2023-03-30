import xarray as xr
import numpy as np
from datetime import datetime
import utils.global_variables as global_vars

def get_variables():
  dataset = global_vars.current_project_dataset
  variables_only = list(dataset.variables.keys())
  for coord in dataset.coords:
    if coord in variables_only:
        variables_only.remove(coord)
  return variables_only

def get_depth_values(name_in_dataset='depth'):
  dataset = global_vars.current_project_dataset
  depth_values = dataset.coords[name_in_dataset].values
  depth_values = [round(depth) for depth in depth_values]
  return depth_values

def get_time_values(name_in_dataset='time'):
  dataset = global_vars.current_project_dataset
  time_values = dataset.coords[name_in_dataset].values
  time_values = [datetime.fromisoformat(np.datetime_as_string(dt, unit='s')) for dt in time_values]
  return time_values
