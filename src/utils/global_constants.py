import pathlib
from utils.general_utils import get_directory_from_config

DATASETS_DIR = get_directory_from_config('DATASETS_DIR')
PROJECTS_DIR = get_directory_from_config('PROJECTS_DIR')

ASSETS_DIR = pathlib.Path(pathlib.Path(__file__).parent.absolute(), '..', 'assets')
