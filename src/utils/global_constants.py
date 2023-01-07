import pathlib
from utils.general_utils import get_directory_from_config

DATASETS_DIR = get_directory_from_config('DATASETS_DIR_FROM_ROOT_PROJECT')
VISUALIZATIONS_DIR = get_directory_from_config('VISUALIZATIONS_DIR_FROM_ROOT_PROJECT')
ASSETS_DIR = pathlib.Path(pathlib.Path(__file__).parent.absolute(), '..', 'assets')
