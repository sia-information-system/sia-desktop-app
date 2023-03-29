import xarray as xr
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