#!/usr/bin/env python3

from datetime import datetime
from calendar import timegm
from cv2 import CAP_V4L2, imwrite, VideoCapture
from face_recognition import face_encodings, load_image_file
from json import dump, load
from numpy import save
from os import getuid, path, remove
from pocketsphinx import get_model_path
from re import compile, findall, sub
from time import gmtime, strptime
from tkinter import BooleanVar, Button, Checkbutton, END, Entry, Frame, Label, LabelFrame, LEFT, Listbox, OptionMenu, StringVar, Text, Tk, TOP

CONFIG_FILE = "config.json"
CONFIG_PATH = "./"
FACES_PATH = CONFIG_PATH + "Faces/"
ENCODED_FACES_PATH = FACES_PATH + "Encoded/"
FACES_EXTENSION = ".jpg"
ENCODED_FACES_EXTENSION = ".npy"
DATE_FORMAT = "%Y-%m-%d"
LANGUAGE_FORMAT = "^[a-z]{2}-[a-z]{2}$"
RED = "\x1b[1;31m"
GREEN = "\x1b[1;32m"
YELLOW = "\x1b[1;33m"
BLUE = "\x1b[1;34m"
DEFAULT = "\x1b[0m"

"""
Checks user's name format.
@param name: User's name
@returns: True if user's name has correct format. False if not or name is empty
"""


def name_format(name):
    if not name or name.isspace():
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Name cannot be empty{DEFAULT}")
        return False
    if not all(char.isalpha() or char.isspace() for char in name):
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Name must have only letters and spaces{DEFAULT}")
        return False
    return True


"""
Checks user's birth date format.
@param birth_date: User's birth date
@returns: True if user's birth date has correct format. False if not or birth date is empty
"""


def birth_date_format(birth_date):
    if not birth_date or birth_date.isspace():
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Birth date cannot be empty{DEFAULT}")
        return False
    try:
        strptime(birth_date.strip(), DATE_FORMAT)
    except ValueError:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Birth date must be in the format yyyy-mm-dd{DEFAULT}")
        return False
    return True


"""
Takes a photo through the camera.
@returns: Taken photo. False if photo could not be taken
"""


def take_photo():
    capture = VideoCapture(CAP_V4L2)
    returned, photo = capture.read()
    capture.release()
    if not returned:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Unable to read camera{DEFAULT}")
        return False
    return photo


"""
Sets a new face.
@returns: Face identifier. False if face could not be seted
"""


def set_face():
    timestamp = str(timegm(gmtime()))
    face = take_photo()
    if face is False:
        return False
    if not imwrite(FACES_PATH + timestamp + FACES_EXTENSION, face):
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Unable to set user's face{DEFAULT}")
        return False
    return timestamp


"""
Creates a new user.
@param name: User's name
@param birth_date: User's birth date
@param language: User's language
@returns: True if the user was created. False if parameters are incomplete or incorrect, user is existing, face could not be seted or face could not be detected
"""


def create_user(name, birth_date, language):
    if not name_format(name) or not birth_date_format(birth_date):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for user in config["users"]:
            if name.strip() == user["name"]:
                print(
                    f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Existing user{DEFAULT}")
                return False
        timestamp = set_face()
        if not timestamp:
            return False
        face = load_image_file(FACES_PATH + timestamp + FACES_EXTENSION)
        try:
            face_encoding = face_encodings(face)[0]
        except IndexError:
            print(
                f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Face could not be detected{DEFAULT}")
            remove(FACES_PATH + timestamp + FACES_EXTENSION)
            return False
        save(ENCODED_FACES_PATH + timestamp +
             ENCODED_FACES_EXTENSION, face_encoding)
        config["users"].append(
            {"name": name.strip(), "birth_date": birth_date.strip(), "language": language, "face": timestamp})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}User created{DEFAULT}")
    return True


"""
Removes a user.
@param name: User's name
@returns: True if the user was removed. False if parameter is incomplete or incorrect or user is not existing
"""


def remove_user(name):
    if not name_format(name):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for user in config["users"]:
            if name.strip() == user["name"]:
                config["users"].remove(user)
                config_file.seek(0)
                dump(config, config_file, indent=4)
                config_file.truncate()
                try:
                    remove(FACES_PATH + user["face"] + FACES_EXTENSION)
                except OSError:
                    pass
                try:
                    remove(ENCODED_FACES_PATH +
                           user["face"] + ENCODED_FACES_EXTENSION)
                except OSError:
                    pass
                print(
                    f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}User removed{DEFAULT}")
                return True
    print(
        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Non existing user{DEFAULT}")
    return False


"""
Checks role format.
@param role: Role
@returns: True if role has correct format. False if not or role is empty
"""


def role_format(role):
    if not role or role.isspace():
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role cannot be empty{DEFAULT}")
        return False
    if not all(char.isalpha() or char.isspace() for char in role):
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role must have only letters and spaces{DEFAULT}")
        return False
    return True


"""
Creates a new role.
@param role: Role
@param age_restriction: Age restriction
@returns: True if the role was created. False if parameter are incomplete or incorrect or role is existing
"""


def create_role(role, age_restriction):
    if not role_format(role):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _role in config["roles"]:
            if role.strip() == _role["role"]:
                print(
                    f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Existing role{DEFAULT}")
                return False
        config["roles"].append(
            {"role": role.strip(), "age_restriction": age_restriction, "users": []})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Role created{DEFAULT}")
    return True


"""
Removes a role.
@param role: Role
@returns: True if the role was removed. False if parameter is incomplete or incorrect or role is not existing
"""


def remove_role(role):
    if not role_format(role):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _role in config["roles"]:
            if role.strip() == _role["role"]:
                config["roles"].remove(_role)
                config_file.seek(0)
                dump(config, config_file, indent=4)
                config_file.truncate()
                print(
                    f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Role removed{DEFAULT}")
                return True
    print(
        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Non existing role{DEFAULT}")
    return False


"""
Assigns a role to a user.
@param role: Role
@param user: User
@returns: True if the role was assigned. False if user is already assigned to this role
"""


def assign_role(role, user):
    if not role:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role cannot be empty{DEFAULT}")
        return False
    if not user:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}User cannot be empty{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _role in config["roles"]:
            if role == _role["role"]:
                if user in _role["users"]:
                    print(
                        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}User already assigned to this role{DEFAULT}")
                    return False
                else:
                    _role["users"].append(user)
                    config_file.seek(0)
                    dump(config, config_file, indent=4)
                    print(
                        f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}User assigned{DEFAULT}")
                    return True


"""
Deassigns a role from a user.
@param role: Role
@param user: User
@returns: True if the role was deassigned.
"""


def deassign_role(role, user):
    if not role:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role cannot be empty{DEFAULT}")
        return False
    if not user:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}User cannot be empty{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _role in config["roles"]:
            if role == _role["role"]:
                if user not in _role["users"]:
                    print(
                        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}User not assigned to this role{DEFAULT}")
                    return False
                else:
                    _role["users"].remove(user)
                    config_file.seek(0)
                    dump(config, config_file, indent=4)
                    config_file.truncate()
                    print(
                        f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}User deassigned{DEFAULT}")
                    return True


"""
Checks command format.
@param command: Command
@returns: True if command is not empty. False if not
"""


def command_format(command):
    if not command or command.isspace():
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Command cannot be empty{DEFAULT}")
        return False
    return True


"""
Checks description format.
@param description: Description
@returns: True if description is not empty. False if not
"""


def description_format(description):
    if not description or description.isspace():
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Description cannot be empty{DEFAULT}")
        return False
    return True


"""
Creates a new command.
@param command: Command
@param description: Command's description
@returns: True if the command was created. False if parameters are incomplete or incorrect or command is existing
"""


def create_command(command, description):
    if not command_format(command) or not description_format(description):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _command in config["commands"]:
            if command.strip() == _command["command"]:
                print(
                    f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Existing command{DEFAULT}")
                return False
        config["commands"].append(
            {"command": command.strip(), "description": description.strip(), "roles": []})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Command created{DEFAULT}")
    return True


"""
Removes a command.
@param command: Command
@returns: True if the command was removed. False if parameter is incomplete or incorrect or command is not existing
"""


def remove_command(command):
    if not command_format(command):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _command in config["commands"]:
            if command.strip() == _command["command"]:
                config["commands"].remove(_command)
                config_file.seek(0)
                dump(config, config_file, indent=4)
                config_file.truncate()
                print(
                    f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Command removed{DEFAULT}")
                return True
    print(
        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Non existing command{DEFAULT}")
    return False


"""
Assigns a role to a command.
@param command: Command
@param role: Role
@returns: True if the role was assigned. False if role is already assigned to this command
"""


def assign_command(command, role):
    if not command:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Command cannot be empty{DEFAULT}")
        return False
    if not role:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role cannot be empty{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _command in config["commands"]:
            if command == _command["command"]:
                if role in _command["roles"]:
                    print(
                        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Role already assigned to this command{DEFAULT}")
                    return False
                else:
                    _command["roles"].append(role)
                    config_file.seek(0)
                    dump(config, config_file, indent=4)
                    print(
                        f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Role assigned{DEFAULT}")
                    return True


"""
Deassigns a role from a command.
@param command: Command
@param role: Role
@returns: True if the role was deassigned. False if role is not assigned to this command
"""


def deassign_command(command, role):
    if not command:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Command cannot be empty{DEFAULT}")
        return False
    if not role:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role cannot be empty{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _command in config["commands"]:
            if command == _command["command"]:
                if role not in _command["roles"]:
                    print(
                        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Role not assigned to this command{DEFAULT}")
                    return False
                else:
                    _command["roles"].remove(role)
                    config_file.seek(0)
                    dump(config, config_file, indent=4)
                    config_file.truncate()
                    print(
                        f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Role deassigned{DEFAULT}")
                    return True


"""
Cheecks response format.
@param response: Response
@returns: True if response has correct format. False if not or response is empty
"""


def response_format(response):
    if not response or response.isspace():
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Response cannot be empty{DEFAULT}")
        return False
    if not all(char.isalpha() or char.isspace() for char in response):
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Response must have only letters and spaces{DEFAULT}")
        return False
    return True


"""
Checks phrases format.
@param phrases: Phrases
@returns: True if phrases have correct format. False if not or phrases are empty
"""


def phrases_format(phrases):
    for phrase in compile(r"[\n\r]+").split(phrases.strip()):
        if not phrase or phrase.isspace():
            print(
                f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Phrases cannot be empty{DEFAULT}")
            return False
        if not all(char.isalpha() or char.isspace() for char in phrase):
            print(
                f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Phrases must have only letters and spaces{DEFAULT}")
            return False
    return True


"""
Counts the number of syllables in a phrase.
@param phrase: Phrase
@returns: Phrase's number of syllables
"""


def get_syllables(phrase):
    syllables = 0
    for word in findall(r"\w+", phrase.lower()):
        syllables += len(findall(r"[aeiou]", word)) - \
            len(findall(r"[aeiou]{2}", word))
    return syllables


"""
Gets the threshold of a phrase.
@param phrase: Phrase
@returns: Phrase's threshold. False if phrase is incorrect or has more than 10 syllables
"""


def get_threshold(phrase):
    syllables = get_syllables(phrase)
    if syllables == 0:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Incorrect phrase{DEFAULT}")
        return False
    elif syllables == 1:
        return 1
    elif syllables == 2:
        return 10
    elif syllables == 3:
        return 15
    elif syllables == 4:
        return 20
    elif syllables == 5:
        return 25
    elif syllables == 6:
        return 30
    elif syllables == 7:
        return 35
    elif syllables == 8:
        return 40
    elif syllables == 9:
        return 45
    elif syllables == 10:
        return 50
    else:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Phrases cannot have more than 10 syllables{DEFAULT}")
        return False


"""
Creates a new phrase.
@param language: Language
@param command: Command
@param response: Response
@param phrases: Phrases
@returns: True if the phrase was created. False if parameters are incomplete or incorrect or command is already configured on this language
"""


def create_phrase(language, command, response, phrases):
    if not command_format(command) or not response_format(response) or not phrases_format(phrases):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _language in config["languages"]:
            if language == _language["language"]:
                for phrase in _language["phrases"]:
                    if command == phrase["command"]:
                        print(
                            f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Command already configured in this language{DEFAULT}")
                        return False
                thresholds = []
                new_phrase = {"command": command,
                              "response": response.strip().lower(), "phrases": []}
                for phrase in compile(r"[\n\r]+").split(phrases.strip().lower()):

                    # TODO: Check if every word exists in dictionary file

                    threshold = get_threshold(phrase)
                    if not threshold:
                        return False
                    if phrase not in new_phrase["phrases"]:
                        new_phrase["phrases"].append(
                            sub(r"\s+\n", "\n", phrase.strip()).strip())
                        thresholds.append(threshold)
                with open(path.join(get_model_path(), language, _language["kws"]), "r+") as list_file:
                    lines = list_file.readlines()
                    index = 0
                    for phrase in new_phrase["phrases"]:
                        phrase_with_threshold = phrase + " /1e-" + \
                            str(thresholds[index]) + "/\n"
                        if phrase_with_threshold not in lines:
                            lines.append(phrase_with_threshold)
                        index += 1
                    list_file.seek(0)
                    list_file.writelines(sorted(lines))
                _language["phrases"].append(new_phrase)
                config_file.seek(0)
                dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Phrase created{DEFAULT}")
    return True


"""
Removes a phrase.
@param language: Language
@param command: Command
@returns: True if the phrase was removed. False if command is not configured on this language
"""


def remove_phrase(language, command):
    if not command_format(command):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _language in config["languages"]:
            if language == _language["language"]:
                for phrase in _language["phrases"]:
                    if command == phrase["command"]:
                        _language["phrases"].remove(phrase)
                        config_file.seek(0)
                        dump(config, config_file, indent=4)
                        config_file.truncate()

                        # TODO: Remove phrases from kws file

                        print(
                            f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Phrase removed{DEFAULT}")
                        return True
    print(
        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Command not configured in this language{DEFAULT}")
    return False


"""
Returns instaled languages.
@returns: A list with installed languages. False if there are no languages
"""


def get_languages_language():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["languages"]) == 0:
            return False
        return [language["language"] for language in config["languages"]]


"""
Returns user's age.
@param birth_date: User's birth date
@returns: User's age
"""


def age(birth_date):
    current_date = datetime.now()
    return current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))


"""
Returns existing users.
@returns: A list with existing users or an array with an empty string if there are no users
"""


def get_users():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["users"]) == 0:
            return [""]
        return [{"name": user["name"], "age": age(datetime.strptime(user["birth_date"], DATE_FORMAT)), "language": user["language"]} for user in config["users"]]


"""
Returns existing roles.
@returns: A list with existing roles or an array with an empty string if there are no roles
"""


def get_roles():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["roles"]) == 0:
            return [""]
        return [{"role": role["role"], "age_restriction": role["age_restriction"]} for role in config["roles"]]


"""
Returns roles and their assigned users.
@returns: A list with roles and a list with its assigned users
"""


def get_roles_users():
    roles, users = [], []
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for role in config["roles"]:
            roles.append(role["role"])
            users.append(role["users"])
    return roles, users


"""
Returns existing commands.
@returns: A list with existing commands or an array with an empty string if there are no commands
"""


def get_commands():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["commands"]) == 0:
            return [""]
        return [{"command": command["command"], "description": command["description"]} for command in config["commands"]]


"""
Returns commands and their assigned roles.
@returns: A list with commands and a list with its assigned roles
"""


def get_commands_roles():
    commands, roles = [], []
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for command in config["commands"]:
            commands.append(command["command"])
            roles.append(command["roles"])
    return commands, roles


"""
Creates a new user in graphical mode.
"""


def gui_create_user():
    name = users_name_entry.get()
    birth_date = users_birth_date_entry.get()
    language = users_language_entry.get()
    create_user(name, birth_date, language)
    gui_update_roles_user_menu()
    gui_update_user_list()


"""
Removes a user in graphical mode.
"""


def gui_remove_user():
    name = users_name_entry.get()
    remove_user(name)
    gui_update_roles_user_menu()
    gui_update_user_list()


"""
Update user's list in graphical mode.
"""


def gui_update_user_list():
    users = get_users()
    users_list.delete(0, END)
    if not users[0]:
        users_list.insert(END, "Non existing users...")
    else:
        for user in users:
            users_list.insert(
                END, user["name"] + " [ " + str(user["age"]) + " years ] [ " + user["language"] + " ]")
    users_list.config(width=max([len(user)
                      for user in users_list.get(0, END)]))
    users_list.config(height=users_list.size())


"""
Update roles's user menu in graphical mode.
"""


def gui_update_roles_user_menu():
    roles_users_user_menu["menu"].delete(0, END)
    users = get_users()
    if users[0]:
        for user in users:
            roles_users_user_menu["menu"].add_command(label=user["name"] + " [ " + str(user["age"]) + " years ] [ " +
                                                      user["language"] + " ]", command=lambda value=user["name"]: roles_users_user_entry.set(value))
        roles_users_user_entry.set(users[0]["name"])
    else:
        roles_users_user_menu["menu"].add_command(
            label=users[0], command=lambda value=users[0]: roles_users_user_entry.set(value))
        roles_users_user_entry.set(users[0])


"""
Creates a new role in graphical mode.
"""


def gui_create_role():
    role = roles_role_entry.get()
    age_restriction = roles_age_restriction_entry.get()
    create_role(role, age_restriction)
    gui_update_roles_role_menu()
    gui_update_commands_role_menu()
    gui_update_role_list()
    gui_update_role_user_list()


"""
Removes a role in graphical mode.
"""


def gui_remove_role():
    role = roles_role_entry.get()
    remove_role(role)
    gui_update_roles_role_menu()
    gui_update_commands_role_menu()
    gui_update_role_list()
    gui_update_role_user_list()


"""
Update role's list in graphical mode.
"""


def gui_update_role_list():
    roles = get_roles()
    roles_list.delete(0, END)
    if not roles[0]:
        roles_list.insert(END, "Non existing roles...")
    else:
        for role in roles:
            roles_list.insert(
                END, role["role"] + " [ age restriction: " + str(role["age_restriction"]) + " ]")
    roles_list.config(width=max([len(role)
                      for role in roles_list.get(0, END)]))
    roles_list.config(height=roles_list.size())


"""
Update roles's assigned users in graphical mode.
"""


def gui_update_role_user_list():
    roles, users = get_roles_users()
    roles_users_list.delete(0, END)
    if not roles:
        roles_users_list.insert(END, "Non existing roles...")
    else:
        for i in range(len(roles)):
            roles_users_list.insert(
                END, roles[i] + " [ " + ", ".join(users[i]) + " ]")
    roles_users_list.config(width=max([len(assignation)
                                       for assignation in roles_users_list.get(0, END)]))
    roles_users_list.config(height=roles_users_list.size())


"""
Update roles's role menu in graphical mode.
"""


def gui_update_roles_role_menu():
    roles_users_role_menu["menu"].delete(0, END)
    roles = get_roles()
    if roles[0]:
        for role in roles:
            roles_users_role_menu["menu"].add_command(label=role["role"] + " [ age restriction: " + str(
                role["age_restriction"]) + " ]", command=lambda value=role["role"]: roles_users_role_entry.set(value))
        roles_users_role_entry.set(roles[0]["role"])
    else:
        roles_users_role_menu["menu"].add_command(
            label=roles[0], command=lambda value=roles[0]: roles_users_role_entry.set(value))
        roles_users_role_entry.set(roles[0])


"""
Assign a role to a user in graphical mode.
"""


def gui_assign_role():
    role = roles_users_role_entry.get()
    user = roles_users_user_entry.get()
    assign_role(role, user)
    gui_update_role_user_list()


"""
Deassign a role to a user in graphical mode.
"""


def gui_deassign_role():
    role = roles_users_role_entry.get()
    user = roles_users_user_entry.get()
    deassign_role(role, user)
    gui_update_role_user_list()


"""
Creates a new command in graphical mode.
"""


def gui_create_command():
    command = commands_command_entry.get()
    description = commands_description_entry.get()
    create_command(command, description)
    gui_update_command_list()
    gui_update_command_role_list()
    gui_update_commands_command_menu()
    gui_update_phrases_command_menu()


"""
Removes a command in graphical mode.
"""


def gui_remove_command():
    command = commands_command_entry.get()
    remove_command(command)
    gui_update_command_list()
    gui_update_command_role_list()
    gui_update_commands_command_menu()
    gui_update_phrases_command_menu()


"""
Update command's list in graphical mode.
"""


def gui_update_command_list():
    commands = get_commands()
    commands_list.delete(0, END)
    if not commands[0]:
        commands_list.insert(END, "Non existing commands...")
    else:
        for command in commands:
            commands_list.insert(
                END, command["command"] + " [ " + command["description"] + " ]")
    commands_list.config(width=max([len(command)
                         for command in commands_list.get(0, END)]))
    commands_list.config(height=commands_list.size())


"""
Update commands's assigned roles in graphical mode.
"""


def gui_update_command_role_list():
    commands, roles = get_commands_roles()
    commands_roles_list.delete(0, END)
    if not commands:
        commands_roles_list.insert(END, "Non existing commands...")
    else:
        for i in range(len(roles)):
            commands_roles_list.insert(
                END, commands[i] + " [ " + ", ".join(roles[i]) + " ]")
    commands_roles_list.config(width=max([len(assignation)
                                          for assignation in commands_roles_list.get(0, END)]))
    commands_roles_list.config(height=commands_roles_list.size())


"""
Update commands's command menu in graphical mode.
"""


def gui_update_commands_command_menu():
    commands_roles_command_menu["menu"].delete(0, END)
    commands = get_commands()
    if commands[0]:
        for command in commands:
            commands_roles_command_menu["menu"].add_command(
                label=command["description"], command=lambda value=command["command"]: commands_roles_command_entry.set(value))
        commands_roles_command_entry.set(commands[0]["command"])
    else:
        commands_roles_command_menu["menu"].add_command(
            label=commands[0], command=lambda value=commands[0]: commands_roles_command_entry.set(value))
        commands_roles_command_entry.set(commands[0])


"""
Update commands's role menu in graphical mode.
"""


def gui_update_commands_role_menu():
    commands_roles_role_menu["menu"].delete(0, END)
    roles = get_roles()
    if roles[0]:
        for role in roles:
            commands_roles_role_menu["menu"].add_command(label=role["role"] + " [ age restriction: " + str(
                role["age_restriction"]) + " ]", command=lambda value=role["role"]: commands_roles_role_entry.set(value))
        commands_roles_role_entry.set(roles[0]["role"])
    else:
        commands_roles_role_menu["menu"].add_command(
            label=roles[0], command=lambda value=roles[0]: commands_roles_role_entry.set(value))
        commands_roles_role_entry.set(roles[0])


"""
Update phrases's command menu in graphical mode.
"""


def gui_update_phrases_command_menu():
    phrases_command_menu["menu"].delete(0, END)
    commands = get_commands()
    if commands[0]:
        for command in commands:
            phrases_command_menu["menu"].add_command(
                label=command["description"], command=lambda value=command["command"]: phrases_command_entry.set(value))
        phrases_command_entry.set(commands[0]["command"])
    else:
        phrases_command_menu["menu"].add_command(
            label=commands[0], command=lambda value=commands[0]: phrases_command_entry.set(value))
        phrases_command_entry.set(commands[0])


"""
Assign a command to a role in graphical mode.
"""


def gui_assign_command():
    command = commands_roles_command_entry.get()
    role = commands_roles_role_entry.get()
    assign_command(command, role)
    gui_update_command_role_list()


"""
Deassign a command to a role in graphical mode.
"""


def gui_deassign_command():
    command = commands_roles_command_entry.get()
    role = commands_roles_role_entry.get()
    deassign_command(command, role)
    gui_update_command_role_list()


"""
Creates a new phrase in graphical mode.
"""


def gui_create_phrase():
    language = phrases_language_entry.get()
    command = phrases_command_entry.get()
    response = phrases_response_entry.get()
    phrases = phrases_phrases_text.get("1.0", END)
    create_phrase(language, command, response, phrases)


"""
Removes phrase in graphical mode.
"""


def gui_remove_phrase():
    language = phrases_language_entry.get()
    command = phrases_command_entry.get()
    remove_phrase(language, command)


if __name__ == "__main__":
    if getuid() != 0:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Run it as root{DEFAULT}")
        exit()
    languages_language = get_languages_language()
    if not languages_language:
        print(
            f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}No languages found{DEFAULT}")
        exit()
    print(
        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Starting settings...{DEFAULT}")
    try:
        root = Tk()
        root.title("Settings")
        users_frame = LabelFrame(root, text="Users", padx=5, pady=5)
        users_frame.pack(side=TOP, padx=10, pady=10)
        users_name_label = Label(users_frame, text="Name")
        users_name_label.pack(side=LEFT, padx=10)
        users_name_entry = Entry(users_frame)
        users_name_entry.pack(side=LEFT, padx=10)
        users_birth_date_label = Label(
            users_frame, text="Birth Date")
        users_birth_date_label.pack(side=LEFT, padx=10)
        users_birth_date_entry = Entry(users_frame)
        users_birth_date_entry.pack(side=LEFT, padx=10)
        users_language_entry = StringVar(root)
        users_language_entry.set(languages_language[0])
        users_language_menu = OptionMenu(
            users_frame, users_language_entry, *languages_language)
        users_language_menu.pack(side=LEFT, padx=10)
        users_create_button = Button(
            users_frame, text="Create", command=gui_create_user)
        users_create_button.pack(side=LEFT, padx=10)
        user_remove_button = Button(
            users_frame, text="Remove", command=gui_remove_user)
        user_remove_button.pack(side=LEFT, padx=10)
        users_list = Listbox(users_frame)
        users_list.pack(side=LEFT, padx=10)
        gui_update_user_list()
        roles_frame = LabelFrame(root, text="Roles", padx=5, pady=5)
        roles_frame.pack(side=TOP, padx=10, pady=10)
        roles_1_frame = Frame(roles_frame)
        roles_1_frame.pack(side=TOP, pady=10)
        roles_role_label = Label(roles_1_frame, text="Role")
        roles_role_label.pack(side=LEFT, padx=10)
        roles_role_entry = Entry(roles_1_frame)
        roles_role_entry.pack(side=LEFT, padx=10)
        roles_age_restriction_entry = BooleanVar()
        roles_age_restriction_check = Checkbutton(
            roles_1_frame, text="Age Restriction", variable=roles_age_restriction_entry)
        roles_age_restriction_check.pack(side=LEFT, padx=10)
        roles_create_button = Button(
            roles_1_frame, text="Create", command=gui_create_role)
        roles_create_button.pack(side=LEFT, padx=10)
        role_remove_button = Button(
            roles_1_frame, text="Remove", command=gui_remove_role)
        role_remove_button.pack(side=LEFT, padx=10)
        roles_list = Listbox(roles_1_frame)
        roles_list.pack(side=LEFT, padx=10)
        gui_update_role_list()
        roles_2_frame = Frame(roles_frame)
        roles_2_frame.pack(side=TOP, pady=10)
        roles_users_role_entry = StringVar(root)
        roles_users_role_menu = OptionMenu(
            roles_2_frame, roles_users_role_entry, "")
        roles_users_role_menu.pack(side=LEFT, padx=10)
        gui_update_roles_role_menu()
        roles_users_user_entry = StringVar(root)
        roles_users_user_menu = OptionMenu(
            roles_2_frame, roles_users_user_entry, "")
        roles_users_user_menu.pack(side=LEFT, padx=10)
        gui_update_roles_user_menu()
        roles_assignment_button = Button(
            roles_2_frame, text="Assign", command=gui_assign_role)
        roles_assignment_button.pack(side=LEFT, padx=10)
        roles_deassignment_button = Button(
            roles_2_frame, text="Deassign", command=gui_deassign_role)
        roles_deassignment_button.pack(side=LEFT, padx=10)
        roles_users_list = Listbox(roles_2_frame)
        roles_users_list.pack(side=LEFT, padx=10)
        gui_update_role_user_list()
        commands_frame = LabelFrame(root, text="Commands", padx=5, pady=5)
        commands_frame.pack(side=TOP, padx=10, pady=10)
        commands_1_frame = Frame(commands_frame)
        commands_1_frame.pack(side=TOP, pady=10)
        commands_command_label = Label(
            commands_1_frame, text="Command")
        commands_command_label.pack(side=LEFT, padx=10)
        commands_command_entry = Entry(commands_1_frame)
        commands_command_entry.pack(side=LEFT, padx=10)
        commands_description_label = Label(
            commands_1_frame, text="Description")
        commands_description_label.pack(side=LEFT, padx=10)
        commands_description_entry = Entry(commands_1_frame)
        commands_description_entry.pack(side=LEFT, padx=10)
        commands_create_button = Button(
            commands_1_frame, text="Create", command=gui_create_command)
        commands_create_button.pack(side=LEFT, padx=10)
        commands_remove_button = Button(
            commands_1_frame, text="Remove", command=gui_remove_command)
        commands_remove_button.pack(side=LEFT, padx=10)
        commands_list = Listbox(commands_1_frame)
        commands_list.pack(side=LEFT, padx=10)
        gui_update_command_list()
        commands_2_frame = Frame(commands_frame)
        commands_2_frame.pack(side=TOP, pady=10)
        commands_roles_command_entry = StringVar(root)
        commands_roles_command_menu = OptionMenu(
            commands_2_frame, commands_roles_command_entry, "")
        commands_roles_command_menu.pack(side=LEFT, padx=10)
        gui_update_commands_command_menu()
        commands_roles_role_entry = StringVar(root)
        commands_roles_role_menu = OptionMenu(
            commands_2_frame, commands_roles_role_entry, "")
        commands_roles_role_menu.pack(side=LEFT, padx=10)
        gui_update_commands_role_menu()
        commands_assignment_button = Button(
            commands_2_frame, text="Assign", command=gui_assign_command)
        commands_assignment_button.pack(side=LEFT, padx=10)
        commands_deassignment_button = Button(
            commands_2_frame, text="Deassign", command=gui_deassign_command)
        commands_deassignment_button.pack(side=LEFT, padx=10)
        commands_roles_list = Listbox(commands_2_frame)
        commands_roles_list.pack(side=LEFT, padx=10)
        gui_update_command_role_list()
        phrases_frame = LabelFrame(root, text="Phrases", padx=5, pady=5)
        phrases_frame.pack(side=TOP, padx=10, pady=10)
        phrases_1_frame = Frame(phrases_frame)
        phrases_1_frame.pack(side=TOP, pady=10)
        phrases_language_entry = StringVar(root)
        phrases_language_entry.set(languages_language[0])
        phrases_language_menu = OptionMenu(
            phrases_1_frame, phrases_language_entry, *languages_language)
        phrases_language_menu.pack(side=LEFT, padx=10)
        phrases_command_entry = StringVar(root)
        phrases_command_menu = OptionMenu(
            phrases_1_frame, phrases_command_entry, "")
        phrases_command_menu.pack(side=LEFT, padx=10)
        gui_update_phrases_command_menu()
        phrases_response_label = Label(
            phrases_1_frame, text="Response")
        phrases_response_label.pack(side=LEFT, padx=10)
        phrases_response_entry = Entry(phrases_1_frame)
        phrases_response_entry.pack(side=LEFT, padx=10)
        phrases_2_frame = Frame(phrases_frame)
        phrases_2_frame.pack(side=TOP, pady=10)
        phrases_phrases_label = Label(
            phrases_2_frame, text="Phrases")
        phrases_phrases_label.pack(side=LEFT, padx=10)
        phrases_phrases_text = Text(phrases_2_frame)
        phrases_phrases_text.pack(side=LEFT, padx=10)
        phrases_create_button = Button(
            phrases_2_frame, text="Create", command=gui_create_phrase)
        phrases_create_button.pack(side=LEFT, padx=10)
        phrases_remove_button = Button(
            phrases_2_frame, text="Remove", command=gui_remove_phrase)
        phrases_remove_button.pack(side=LEFT, padx=10)
        root.mainloop()
    except KeyboardInterrupt:
        print("[*] Exiting settings...")
