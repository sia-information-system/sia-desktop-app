from pathlib import Path
from utils.general_utils import get_directory_from_config, get_app_root_dir

ASSETS_DIR = Path(get_app_root_dir(), 'assets')
TMP_DIR = Path(get_app_root_dir(), 'tmp')

HOME_DIRNAME = 'SIA'
HOME_DIR = Path(Path.home(), HOME_DIRNAME)
HOME_DATASETS_DIR = get_directory_from_config('HOME_DATASETS_DIR', start_from='user_home')
HOME_PROJECTS_DIR = get_directory_from_config('HOME_PROJECTS_DIR', start_from='user_home')

PROJECT_EXTENSION = '.sia'
