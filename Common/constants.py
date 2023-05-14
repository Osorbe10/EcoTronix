from os import path

CONFIG_FILE = "config.json"
PERIPHERALS_FILE = "peripherals.json"
PICO_CONFIG_FILE = "config.json"
PICO_CONFIG_TEMPLATE_FILE = "config_template.json"
PICO_SETUP_FILE = "setup.sh"

CONFIG_PATH = path.dirname(path.abspath(__file__)) + "/../"
FACES_PATH = CONFIG_PATH + "Faces/"
ENCODED_FACES_PATH = FACES_PATH + "Encoded/"
LANGUAGES_PATH = CONFIG_PATH + "Languages/"
PICO_PATH = CONFIG_PATH + "Pico/"
PICO_CODES_PATH = PICO_PATH + "Codes/"

FACES_EXTENSION = ".jpg"
ENCODED_FACES_EXTENSION = ".npy"

DATE_FORMAT = "%d-%m-%Y"
LANGUAGE_FORMAT = "^[a-z]{2}-[a-z]{2}$"

COMMAND_TIMEOUT = 10

BLUE = "\x1b[1;34m"
DEFAULT = "\x1b[0m"
GREEN = "\x1b[1;32m"
RED = "\x1b[1;31m"
YELLOW = "\x1b[1;33m"
