import xarray as xr
import numpy as np
from datetime import datetime
import utils.global_variables as global_vars

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

def get_depth_values():
  depth_dim = global_vars.depth_dim
  dataset = global_vars.current_project_dataset
  depth_values = dataset.coords[depth_dim].values
  depth_values = [round(depth, 3) for depth in depth_values]
  return depth_values

def get_time_values():
  time_dim = global_vars.time_dim
  dataset = global_vars.current_project_dataset
  time_values = dataset.coords[time_dim].values
  time_values = [datetime.fromisoformat(np.datetime_as_string(dt, unit='s')) for dt in time_values]
  return time_values

def get_longitude_values():
  lon_dim = global_vars.lon_dim
  dataset = global_vars.current_project_dataset
  longitude_values = dataset.coords[lon_dim].values
  return longitude_values

def get_latitude_values():
  lat_dim = global_vars.lat_dim
  dataset = global_vars.current_project_dataset
  latitude_values = dataset.coords[lat_dim].values
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
      var_attrs = variable.attrs
      if 'unit_long' in var_attrs:
        variables_units[varname] = var_attrs['unit_long']
      elif 'units' in var_attrs:
        variables_units[varname] = var_attrs['units']
      else:
        variables_units[varname] = 'NA'
  return variables_units

def get_dimensions_units():
  dataset = global_vars.current_project_dataset
  dims_units = {}
  for dim in dataset.dims:
    if dim in dataset.coords:
      dim_attrs = dataset.coords[dim].attrs
      if 'unit_long' in dim_attrs:
        dims_units[dim] = dim_attrs['unit_long']
      elif 'units' in dim_attrs:
        dims_units[dim] = dim_attrs['units']
      else:
        dims_units[dim] = 'NA'
  return dims_units

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