import logging
import pathlib
from os import environ

log = logging.getLogger("mocksha")
logging.root.setLevel(logging.INFO)
logging.root.addHandler(logging.StreamHandler())

BASE_DIR = pathlib.Path(__file__).parent
CONFIG_DIR = BASE_DIR / "config_dir"
pathlib.Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)

UPSTREAM = environ.get("UPSTREAM")
