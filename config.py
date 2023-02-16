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
from tkinter import Button, END, Entry, Frame, Label, LabelFrame, LEFT, Listbox, OptionMenu, StringVar, Text, Tk, TOP

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
                    f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Existing user")
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
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}User created")
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
            {"command": command.strip(), "description": description.strip()})
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
        print(phrase)
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
Creates a new user in graphical mode.
"""


def gui_create_user():
    name = users_name_entry.get()
    birth_date = users_birth_date_entry.get()
    language = users_language_entry.get()
    create_user(name, birth_date, language)
    gui_update_user_list()


"""
Removes a user in graphical mode.
"""


def gui_remove_user():
    name = users_name_entry.get()
    remove_user(name)
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
Creates a new command in graphical mode.
"""


def gui_create_command():
    command = commands_command_entry.get()
    description = commands_description_entry.get()
    create_command(command, description)
    gui_update_command_list()
    gui_update_phrases_command_menu()


"""
Removes a command in graphical mode.
"""


def gui_remove_command():
    command = commands_command_entry.get()
    remove_command(command)
    gui_update_command_list()
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
Update phrases's command menu in graphical mode.
"""


def gui_update_phrases_command_menu():
    global commands_command, commands_description
    commands = get_commands()
    commands_command, commands_description = [], []
    if commands[0]:
        for command in commands:
            commands_command.append(command["command"])
            commands_description.append(command["description"])
    else:
        commands_command.append(commands[0])
        commands_description.append(commands[0])
    phrases_command_menu["menu"].delete(0, END)
    for index in range(len(commands_command)):
        phrases_command_menu["menu"].add_command(
            label=commands_description[index], command=lambda value=commands_command[index]: phrases_command_entry.set(value))
    phrases_command_entry.set(commands_command[0])


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


"""
Main function.
"""

if getuid() != 0:
    print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Run it as root{DEFAULT}")
    exit()
languages_language = get_languages_language()
if not languages_language:
    print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}No languages found{DEFAULT}")
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
    commands_frame = LabelFrame(root, text="Commands", padx=5, pady=5)
    commands_frame.pack(side=TOP, padx=10, pady=10)
    commands_command_label = Label(
        commands_frame, text="Command")
    commands_command_label.pack(side=LEFT, padx=10)
    commands_command_entry = Entry(commands_frame)
    commands_command_entry.pack(side=LEFT, padx=10)
    commands_description_label = Label(
        commands_frame, text="Description")
    commands_description_label.pack(side=LEFT, padx=10)
    commands_description_entry = Entry(commands_frame)
    commands_description_entry.pack(side=LEFT, padx=10)
    commands_create_button = Button(
        commands_frame, text="Create", command=gui_create_command)
    commands_create_button.pack(side=LEFT, padx=10)
    commands_remove_button = Button(
        commands_frame, text="Remove", command=gui_remove_command)
    commands_remove_button.pack(side=LEFT, padx=10)
    commands_list = Listbox(commands_frame)
    commands_list.pack(side=LEFT, padx=10)
    gui_update_command_list()
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
    commands_command, commands_description = [], []
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
