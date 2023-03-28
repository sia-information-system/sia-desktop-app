import pathlib
from utils.general_utils import get_directory_from_config

ASSETS_DIR = pathlib.Path(pathlib.Path(__file__).parent.absolute(), '..', '..', 'assets')
TMP_DIR = pathlib.Path(pathlib.Path(__file__).parent.absolute(), '..', '..', 'tmp')

HOME_DIRNAME = 'SIA'
HOME_DIR = pathlib.Path(pathlib.Path.home(), HOME_DIRNAME)
HOME_DATASETS_DIR = get_directory_from_config('HOME_DATASETS_DIR', start_from='user_home')
HOME_PROJECTS_DIR = get_directory_from_config('HOME_PROJECTS_DIR', start_from='user_home')

PROJECT_EXTENSION = '.sia'