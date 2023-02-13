#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from calendar import timegm
from cv2 import CAP_V4L2, imwrite, VideoCapture
from face_recognition import face_encodings, load_image_file
from json import dump, load, loads
from numpy import save
from os import remove
from re import compile
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

"""
Checks user's name format.
@param name: User's name
@returns: True if user's name has correct format. False if not
"""


def name_format(name):
    if not name.isalpha():
        print("[-] Name must have only letters")
        return False
    return True


"""
Checks user's birth date format.
@param birth_date: User's birth date
@returns: True if user's birth date has correct format. False if not
"""


def birth_date_format(birth_date):
    try:
        strptime(birth_date, DATE_FORMAT)
    except ValueError:
        print("[-] Birth date must be in the format yyyy-mm-dd")
        return False
    return True


"""
Checks user's language format.
@param language: User's language
@returns: True if user's language has correct format. False if not
"""


def language_format(language):
    if not compile(LANGUAGE_FORMAT).match(language):
        print("[-] Language must me in the format ll-ll")
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
        print("[-] Unable to read camera")
        return False
    return photo


"""
Sets a new face.
@returns: Face identifier. False if face could not be seted
"""


def set_face():
    timestamp = str(timegm(gmtime()))
    face = take_photo()
    if face is False or not imwrite(FACES_PATH + timestamp + FACES_EXTENSION, face):
        print("[-] Unable to set user's face")
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
    if not name or not birth_date or not language:
        print("[-] Name, birth date and language cannot be empty")
        return False
    if not name_format(name) or not birth_date_format(birth_date) or not language_format(language):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for user in config["users"]:
            if name == user["name"]:
                print("[*] Existing user")
                return False
        timestamp = set_face()
        if not timestamp:
            return False
        face = load_image_file(FACES_PATH + timestamp + FACES_EXTENSION)
        try:
            face_encoding = face_encodings(face)[0]
        except IndexError:
            print("[-] Face could not be detected")
            remove(FACES_PATH + timestamp + FACES_EXTENSION)
            return False
        save(ENCODED_FACES_PATH + timestamp +
             ENCODED_FACES_EXTENSION, face_encoding)
        config["users"].append(
            {"name": name, "birth_date": birth_date, "language": language, "face": timestamp})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print("[+] User created")
    return True


"""
Removes a user.
@param name: User's name
@returns: True if the user was removed. False if parameter is incomplete or incorrect or user is not existing
"""


def remove_user(name):
    if not name:
        print("[-] Name cannot be empty")
        return False
    if not name_format(name):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for user in config["users"]:
            if name == user["name"]:
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
                print("[+] User removed")
                return True
    print("[*] Non existing user")
    return False


"""
Creates a new command.
@param command: Command
@param description: Command's description
@returns: True if the command was created. False if command is incomplete or existing
"""


def create_command(command, description):
    if not command or not description:
        print("[-] Command and description cannot be empty")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _command in config["commands"]:
            if command == _command["command"]:
                print("[*] Existing command")
                return False
        config["commands"].append(
            {"command": command, "description": description})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print("[+] Command created")
    return True


"""
Removes a command.
@param command: Command
@returns: True if the command was removed. False if parameter is incomplete or command is not existing
"""


def remove_command(command):
    if not command:
        print("[-] Command cannot be empty")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _command in config["commands"]:
            if command == _command["command"]:
                config["commands"].remove(_command)
                config_file.seek(0)
                dump(config, config_file, indent=4)
                config_file.truncate()
                print("[+] Command removed")
                return True
    print("[*] Non existing command")
    return False


"""
Creates a new phrase.
@param language: Language
@param command: Command
@param response: Response
@param phrases: Phrases
@returns: True if the phrase was created. False if language is not existing
"""


def create_phrase(language, command, response, phrases):
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _language in config["languages"]:
            if language == _language["language"]:
                new_phrase = {"command": loads(command.replace("'", "\""))["command"],
                              "response": response, "phrases": []}
                for phrase in compile(r"[\n\r]+").split(phrases):
                    if phrase.strip() != "":
                        new_phrase["phrases"].append(phrase.strip())
                _language["phrases"].append(new_phrase)
                config_file.seek(0)
                dump(config, config_file, indent=4)

                # TODO: Add phrases to .list file of that language

                print("[+] Phrase created")
                return True
    print("[*] Non existing language")
    return False


"""
Removes a phrase.
@param language: Language
@param command: Command
@returns: True if the phrase was removed. False if language or command is not existing
"""


def remove_phrase(language, command):
    pass
    # TODO


"""
Returns instaled languages.
@returns: A list with installed languages or an array with an empty string if there are no languages
"""


def get_languages():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["languages"]) == 0:
            return [""]
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
Creates a new user in terminal mode.
@param name: User's name
@param birth_date: User's birth date
@param language: User's language
"""


def cli_create_user(name, birth_date, language):
    create_user(name, birth_date, language)


"""
Removes a user in terminal mode.
@param name: User's name
"""


def cli_remove_user(name):
    remove_user(name)


"""
List users in terminal mode.
"""


def cli_list_users():
    for user in get_users():
        print(user)


"""
Creates a new command in terminal mode.
@param command: Command
@param description: Command's description
"""


def cli_create_command(command, description):
    create_command(command, description)


"""
Removes a command in terminal mode.
@param command: Command
"""


def cli_remove_command(command):
    remove_command(command)


"""
List commands in terminal mode.
"""


def cli_list_commands():
    for command in get_commands():
        print(command)


"""
Creates a new phrase in terminal mode.
@param language: Language
@param command: Command
@param response: Response
@param phrases: Phrases
"""


def cli_create_phrase(language, command, response, phrases):
    create_phrase(language, command, response, phrases)


"""
Removes a phrase in terminal mode.
@param language: Language
@param command: Command
"""


def cli_remove_phrase(language, command):
    remove_phrase(language, command)


"""
List phrases in terminal mode.
@param language: Language
"""


def cli_list_phrases(language):
    pass
    # TODO


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
    if len(users) == 1 and users[0] == "":
        return
    users_list.delete(0, END)
    for user in users:
        users_list.insert(
            END, user["name"] + " [ " + str(user["age"]) + " years ] [ " + user["language"] + " ]")
    try:
        users_list.config(width=max([len(user)
                                     for user in users_list.get(0, END)]))
    except ValueError:
        pass
    users_list.config(height=users_list.size())


"""
Creates a new command in graphical mode.
"""


def gui_create_command():
    command = commands_command_entry.get()
    description = commands_description_entry.get()
    create_command(command, description)
    gui_update_phrases_command_menu()
    gui_update_command_list()


"""
Removes a command in graphical mode.
"""


def gui_remove_command():
    command = commands_command_entry.get()
    remove_command(command)
    gui_update_phrases_command_menu()
    gui_update_command_list()


"""
Update phrases's command menu in graphical mode.
"""


def gui_update_phrases_command_menu():
    pass
    # TODO


"""
Update command's list in graphical mode.
"""


def gui_update_command_list():
    commands = get_commands()
    if len(commands) == 1 and commands[0] == "":
        return
    commands_list.delete(0, END)
    for command in commands:
        commands_list.insert(
            END, command["command"] + " [ " + command["description"] + " ]")
    try:
        commands_list.config(width=max([len(command)
                                        for command in commands_list.get(0, END)]))
    except ValueError:
        pass
    commands_list.config(height=commands_list.size())


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
    pass
    # TODO


"""
Updates phrases's list in graphical mode.
"""


def gui_update_phrases_list():
    pass
    # TODO


if __name__ == "__main__":
    try:
        languages = get_languages()
        commands = get_commands()
        parser = ArgumentParser(description="Settings")
        parser.add_argument(
            "--no-gui", help="Run without GUI on CLI mode", action="store_true")
        parser.add_argument("--type", help="Type of data",
                            choices=["user", "command"])
        parser.add_argument("--action", help="Action to perform",
                            choices=["create", "list", "remove"])
        parser.add_argument("--name", help="User's name")
        parser.add_argument("--birth-date", help="User's birth date")
        parser.add_argument(
            "--language", help="User's language", choices=languages)
        parser.add_argument("--command", help="Shell command")
        parser.add_argument("--description", help="Command's description")
        args = parser.parse_args()
        if args.no_gui:
            print("[*] Starting settings in CLI mode...")
            if args.type == "user":
                if args.action == "create":
                    cli_create_user(args.name, args.birth_date, args.language)
                elif args.action == "list":
                    cli_list_users()
                elif args.action == "remove":
                    cli_remove_user(args.name)
                else:
                    print("[*] No action specified")
            elif args.type == "command":
                if args.action == "create":
                    cli_create_command(args.command, args.description)
                elif args.action == "list":
                    cli_list_commands()
                elif args.action == "remove":
                    cli_remove_command(args.command)
                else:
                    print("[*] No action specified")
            else:
                print("[*] No type specified")
        else:
            print("[*] Starting settings in GUI mode...")
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
            users_language_entry.set(languages[0])
            users_language_menu = OptionMenu(
                users_frame, users_language_entry, *languages)
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
            phrases_language_entry.set(languages[0])
            phrases_language_menu = OptionMenu(
                phrases_1_frame, phrases_language_entry, *languages)
            phrases_language_menu.pack(side=LEFT, padx=10)
            phrases_command_entry = StringVar(root)
            phrases_command_entry.set(commands[0])
            phrases_command_menu = OptionMenu(
                phrases_1_frame, phrases_command_entry, *commands)
            phrases_command_menu.pack(side=LEFT, padx=10)
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
