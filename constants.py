CONFIG_FILE = "config.json"
PICO_SETUP = "setup.sh"

CONFIG_PATH = "./"
FACES_PATH = CONFIG_PATH + "Faces/"
ENCODED_FACES_PATH = FACES_PATH + "Encoded/"
LANGUAGES_PATH = CONFIG_PATH + "Languages/"
PICO_PATH = CONFIG_PATH + "Pico/"

FACES_EXTENSION = ".jpg"
ENCODED_FACES_EXTENSION = ".npy"

DATE_FORMAT = "%Y-%m-%d"
LANGUAGE_FORMAT = "^[a-z]{2}-[a-z]{2}$"

POSITIONS_IN_ROOM = ["Entrance", "Center", "Back"]

BLUE = "\x1b[1;34m"
DEFAULT = "\x1b[0m"
GREEN = "\x1b[1;32m"
RED = "\x1b[1;31m"
YELLOW = "\x1b[1;33m"
