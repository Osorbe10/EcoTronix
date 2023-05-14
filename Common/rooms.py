from Common.constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, GREEN, RED
from json import dump, load

"""
Checks room format.
@param room: Room
@returns: True if room has correct format. False if not or is empty
"""

def room_format(room):
    if not room or room.isspace():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Room cannot be empty{DEFAULT}")
        return False
    if not all(char.isalpha() or char.isspace() for char in room):
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Room must have only letters and spaces{DEFAULT}")
        return False
    return True

"""
Gets a room from config file.
@param room: Room
@returns: Room if is existing. False if not
"""

def get_room(room):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_room in config["rooms"]:
            if room.strip().lower() == config_room["room"].lower():
                return config_room
    return False

"""
Creates a room.
@param room: Room
@returns: True if the room was created. False if room is incomplete or incorrect or room is existing
"""

def create_room(room):
    if not room_format(room):
        return False
    config_room = get_room(room)
    if config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing room{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["rooms"].append({"room": room.strip().capitalize(), "devices": []})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Room created{DEFAULT}")
    return True

"""
Edits a room.
@param old_room: Old room
@param new_room: New room
@returns: True if the room was edited. False if both rooms are incomplete or incorrect or old room is not existing or new room is existing or room has no changes
"""

def edit_room(old_room, new_room):
    if not room_format(old_room) or not room_format(new_room):
        return False
    config_room = get_room(new_room)
    if config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing new room{DEFAULT}")
        return False
    config_room = get_room(old_room)
    if not config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing old room{DEFAULT}")
        return False
    if config_room["room"] == new_room.strip().capitalize():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Room has no changes{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_room in config["rooms"]:
            if config_room["room"] == _config_room["room"]:
                _config_room["room"] = new_room.strip().capitalize()
                for config_device in _config_room["devices"]:
                    config_device["installed"] = False
                break
        for config_command in config["commands"]["remote"]:
            if config_room["room"] == config_command["room"]:
                config_command["room"] = new_room.strip().capitalize()
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Room edited{DEFAULT}")
    return True

"""
Removes a room.
@param room: Room
@returns: True if the room was removed. False if room is incomplete or incorrect or room is not existing
"""

def remove_room(room):
    if not room_format(room):
        return False
    config_room = get_room(room)
    if not config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing room{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["rooms"].remove(config_room)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Room removed{DEFAULT}")
    return True

"""
Gets existing rooms.
@returns: A list with rooms. False if there are no rooms
"""

def get_rooms():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["rooms"]) == 0:
            return False
        return [config_room["room"] for config_room in config["rooms"]]
