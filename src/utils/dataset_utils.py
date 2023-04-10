import xarray as xr
import numpy as np
from datetime import datetime
import utils.global_variables as global_vars

def is_dataset_loaded():
  return global_vars.current_project_dataset is not None

def get_dimensions():
  dataset = global_vars.current_project_dataset
  if not dataset:
    return []
  return list(dataset.dims.keys())

def get_variables():
  dataset = global_vars.current_project_dataset
  if not dataset:
    return []
  variables_only = list(dataset.variables.keys())
  for coord in dataset.coords:
    if coord in variables_only:
        variables_only.remove(coord)
  return variables_only

def get_depth_values(name_in_dataset='depth'):
  dataset = global_vars.current_project_dataset
  depth_values = dataset.coords[name_in_dataset].values
  depth_values = [round(depth, 3) for depth in depth_values]
  return depth_values

def get_time_values(name_in_dataset='time'):
  dataset = global_vars.current_project_dataset
  time_values = dataset.coords[name_in_dataset].values
  time_values = [datetime.fromisoformat(np.datetime_as_string(dt, unit='s')) for dt in time_values]
  return time_values

def get_longitude_values(name_in_dataset='longitude'):
  dataset = global_vars.current_project_dataset
  longitude_values = dataset.coords[name_in_dataset].values
  return longitude_values

def get_latitude_values(name_in_dataset='latitude'):
  dataset = global_vars.current_project_dataset
  latitude_values = dataset.coords[name_in_dataset].values
  return latitude_values

def get_variables_long_names():
  dataset = global_vars.current_project_dataset
  variables_long_names = {}
  for varname, variable in dataset.variables.items():
    if varname not in dataset.coords:
      variable_long_name = variable.attrs['long_name']
      if variable_long_name:
        variables_long_names[variable_long_name] = varname
  return variables_long_names

def get_variables_units():
  dataset = global_vars.current_project_dataset
  variables_units = {}
  for varname, variable in dataset.variables.items():
    if varname not in dataset.coords:
      unit_long = variable.attrs['unit_long']
      units = variable.attrs['units']
      variables_units[varname] = unit_long if unit_long else units
  return variables_units

def get_dataset_info():
  dataset = global_vars.current_project_dataset

  if dataset is None:
    return 'No hay un conjunto de datos cargado'

  dataset_info_text = 'DATOS GENERALES\n\n'
  ds_dict = dataset.attrs
  for key in ds_dict:
    dataset_info_text += f'{key}: {ds_dict[key]}\n'

  dataset_info_text += '\nDIMENSIONES\n\n'

  dataset_info_text += 'Dimensión - Cantidad de valores\n'
  for key in dataset.dims:
    dataset_info_text += f'{key} - {dataset.dims[key]}\n'
  dataset_info_text += '\n'
    
  for coord in dataset.coords:
    dataset_info_text += f'Dimensión: {coord}\n'
    coord_meta = dataset.coords[coord].attrs
    
    for key in coord_meta:
      dataset_info_text += f'\t{key}: {coord_meta[key]}\n'

  dataset_info_text += '\nVARIABLES\n\n'

  ds_coords = dataset.coords
  for varname, variable in dataset.variables.items():
    if varname not in ds_coords:
      dataset_info_text += f'Variable: {varname}\n'
      dataset_info_text += f'\tDimensiones: {variable.dims}\n'
      dataset_info_text += f'\tMetadatos:\n'
      for key in variable.attrs:
        dataset_info_text += f'\t\t{key}: {variable.attrs[key]}\n'

  return dataset_info_text