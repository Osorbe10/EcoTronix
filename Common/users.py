from calendar import timegm
from Common.constants import BLUE, CONFIG_FILE, CONFIG_PATH, DATE_FORMAT, DEFAULT, ENCODED_FACES_EXTENSION, ENCODED_FACES_PATH, FACES_EXTENSION, FACES_PATH, GREEN, RED
from cv2 import CAP_V4L2, imwrite, VideoCapture
from datetime import datetime
from face_recognition import face_encodings, load_image_file
from json import dump, load
from numpy import save
from os import remove
from time import gmtime, strptime

"""
Checks name format.
@param name: Name
@returns: True if name has correct format. False if not or is empty
"""

def name_format(name):
    if not name or name.isspace():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Name cannot be empty{DEFAULT}")
        return False
    if not all(char.isalpha() or char.isspace() for char in name):
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Name must have only letters and spaces{DEFAULT}")
        return False
    return True

"""
Checks birth date format.
@param birth_date: Birth date
@returns: True if birth date has correct format. False if not or is empty
"""

def birth_date_format(birth_date):
    if not birth_date or birth_date.isspace():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Birth date cannot be empty{DEFAULT}")
        return False
    try:
        strptime(birth_date.strip(), DATE_FORMAT)
    except ValueError:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Birth date must be in the format {DATE_FORMAT}{DEFAULT}")
        return False
    return True

"""
Takes a photo through the camera.
@returns: Taken photo. False if could not be taken
"""

def take_photo():
    capture = VideoCapture(CAP_V4L2)
    returned, photo = capture.read()
    capture.release()
    if not returned:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Unable to read camera{DEFAULT}")
        return False
    return photo

"""
Stores a photo.
@returns: Photo identifier. False if could not be stored
"""

def store_photo():
    timestamp = str(timegm(gmtime()))
    face = take_photo()
    if face is False:
        return False
    if not imwrite(FACES_PATH + timestamp + FACES_EXTENSION, face):
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Unable to store photo{DEFAULT}")
        return False
    return timestamp

"""
Gets a user from config file.
@param name: Name
@returns: User if is existing. False if not
"""

def get_user(name):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_user in config["users"]:
            if name.strip().lower() == config_user["name"].lower():
                return config_user
    return False

"""
Creates a user.
@param name: Name
@param birth_date: Birth date
@returns: True if the user was created. False if name or birth date are incomplete or incorrect, user is existing, photo could not be stored or face could not be detected
"""

def create_user(name, birth_date):
    if not name_format(name) or not birth_date_format(birth_date):
        return False
    config_user = get_user(name)
    if config_user:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing user{DEFAULT}")
        return False
    timestamp = store_photo()
    if not timestamp:
        return False
    try:
        face_encoding = face_encodings(load_image_file(FACES_PATH + timestamp + FACES_EXTENSION))[0]
    except IndexError:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Face could not be detected{DEFAULT}")
        try:
            remove(FACES_PATH + timestamp + FACES_EXTENSION)
        except OSError:
            pass
        return False
    save(ENCODED_FACES_PATH + timestamp + ENCODED_FACES_EXTENSION, face_encoding)
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["users"].append({"name": name.strip().capitalize(), "birth_date": birth_date.strip(), "face": timestamp.strip()})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}User created{DEFAULT}")
    return True

"""
Edits a user.
@param old_name: Old name
@param new_name: New name
@param new_birth_date: New birth date
@returns: True if the user was edited. False if both names or birth date are incomplete or incorrect or old user is not existing or new user is existing or user has no changes
"""

def edit_user(old_name, new_name, new_birth_date):
    if not name_format(old_name) or not name_format(new_name) or not birth_date_format(new_birth_date):
        return False
    config_user = get_user(new_name)
    if config_user and old_name.strip().lower() != new_name.strip().lower():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing new user{DEFAULT}")
        return False
    config_user = get_user(old_name)
    if not config_user:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing old user{DEFAULT}")
        return False
    if config_user["name"] == new_name.strip().capitalize() and config_user["birth_date"] == new_birth_date.strip():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}User has no changes{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_user in config["users"]:
            if config_user["name"] == _config_user["name"]:
                _config_user["name"] = new_name.strip().capitalize()
                _config_user["birth_date"] = new_birth_date.strip()
                break
        for _config_role in config["roles"]:
            if config_user["name"] in _config_role["users"]:
                _config_role["users"][_config_role["users"].index(config_user["name"])] = new_name.strip().capitalize()
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}User edited{DEFAULT}")
    return True

"""
Edits a user face.
@param name: Name
@returns: True if the user face was edited. False if name is incomplete or incorrect or user is not existing or photo could not be stored or face could not be detected
"""

def edit_user_face(name):
    if not name_format(name):
        return False
    config_user = get_user(name)
    if not config_user:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing user{DEFAULT}")
        return False
    timestamp = store_photo()
    if not timestamp:
        return False
    try:
        face_encoding = face_encodings(load_image_file(FACES_PATH + timestamp + FACES_EXTENSION))[0]
    except IndexError:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Face could not be detected{DEFAULT}")
        try:
            remove(FACES_PATH + timestamp + FACES_EXTENSION)
        except OSError:
            pass
        return False
    save(ENCODED_FACES_PATH + timestamp + ENCODED_FACES_EXTENSION, face_encoding)
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_user in config["users"]:
            if config_user["name"] == _config_user["name"]:
                _config_user["face"] = timestamp.strip()
                break
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}User face edited{DEFAULT}")
    return True

"""
Removes a user.
@param name: Name
@returns: True if the user was removed. False if name is incomplete or incorrect or user is not existing
"""

def remove_user(name):
    if not name_format(name):
        return False
    config_user = get_user(name)
    if not config_user:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing user{DEFAULT}")
        return False
    deassign_roles(config_user["name"])
    try:
        remove(FACES_PATH + config_user["face"] + FACES_EXTENSION)
        remove(ENCODED_FACES_PATH + config_user["face"] + ENCODED_FACES_EXTENSION)
    except OSError:
        pass
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["users"].remove(config_user)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}User removed{DEFAULT}")
    return True

"""
Deassigns roles from user.
@param name: Name
"""

def deassign_roles(name):
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_role in config["roles"]:
            if name in config_role["users"]:
                config_role["users"].remove(name)
                config_file.seek(0)
                dump(config, config_file, indent=4)
                config_file.truncate()

"""
Returns user's age.
@param birth_date: Birth date
@returns: User's age
"""

def age(birth_date):
    birth_date = datetime.strptime(birth_date, DATE_FORMAT)
    current_date = datetime.now()
    return current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))

"""
Gets existing users.
@returns: A dictionary with name, age and face timestamp for each user. False if there are no users
"""

def get_users():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["users"]) == 0:
            return False
        return [{"name": config_user["name"], "age": age(config_user["birth_date"]), "face": config_user["face"]} for config_user in config["users"]]

"""
Gets user permissions depending on his roles.
@param name: Name
@returns: A dictionary with age restricion and privileged. False if name is incomplete or incorrect or user is not existing
"""

def get_user_permissions(name):
    if not name_format(name):
        return False
    config_user = get_user(name)
    if not config_user:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing user{DEFAULT}")
        return False
    age_restriction = False
    privileged = False
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_role in config["roles"]:
            for user in config_role["users"]:
                if user == name:
                    if config_role["age_restriction"]:
                        age_restriction = True
                    if config_role["privileged"]:
                        privileged = True
                    if age_restriction and privileged:
                        break
    return {"age_restriction": age_restriction, "privileged": privileged}