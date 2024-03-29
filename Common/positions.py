from Common.constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, GREEN, RED
from json import dump, load

"""
Checks position format.
@param position: Position
@returns: True if position has correct format. False if not or is empty
"""

def position_format(position):
    if not position or position.isspace():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Position cannot be empty{DEFAULT}")
        return False
    if not all(char.isalpha() or char.isspace() for char in position):
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Position must have only letters and spaces{DEFAULT}")
        return False
    return True

"""
Gets a position from config file.
@param position: Position
@returns: Position if is existing. False if not
"""

def get_position(position):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_position in config["positions"]:
            if position.strip().lower() == config_position.lower():
                return config_position
    return False

"""
Creates a position.
@param position: Position
@returns: True if the position was created. False if position is incomplete or incorrect or position is existing
"""

def create_position(position):
    if not position_format(position):
        return False
    config_position = get_position(position)
    if config_position:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing position{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["positions"].append(position.strip().capitalize())
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Position created{DEFAULT}")
    return True

"""
Edits a position.
@param old_position: Old position
@param new_position: New position
@returns: True if the position was edited. False if both positions are incomplete or incorrect or old position is not existing or new position is existing or position has no changes
"""

def edit_position(old_position, new_position):
    if not position_format(old_position) or not position_format(new_position):
        return False
    config_position = get_position(new_position)
    if config_position:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing new position{DEFAULT}")
        return False
    config_position = get_position(old_position)
    if not config_position:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing old position{DEFAULT}")
        return False
    if config_position == new_position.strip().capitalize():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Position has no changes{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for index in range(len(config["positions"])):
            if config_position == config["positions"][index]:
                config["positions"][index] = new_position.strip().capitalize()
                break
        for config_room in config["rooms"]:
            for config_device in config_room["devices"]:
                if config_position == config_device["position"]:
                    config_device["position"] = new_position.strip().capitalize()
                    config_device["installed"] = False
        for config_command in config["commands"]["remote"]:
            if config_position == config_command["position"]:
                config_command["position"] = new_position.strip().capitalize()
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Position edited{DEFAULT}")
    return True

"""
Removes a position.
@param position: Position
@returns: True if the position was removed. False if position is incomplete or incorrect or position is not existing
"""

def remove_position(position):
    if not position_format(position):
        return False
    config_position = get_position(position)
    if not config_position:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing position{DEFAULT}")
        return False
    remove_devices(config_position)
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["positions"].remove(config_position)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Position removed{DEFAULT}")
    return True

"""
Removes devices on position.
@param position: Position
"""

def remove_devices(position):
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_room in config["rooms"]:
            for config_device in config_room["devices"]:
                if position == config_device["position"]:
                    config_room["devices"].remove(config_device)
                    config_file.seek(0)
                    dump(config, config_file, indent=4)
                    config_file.truncate()

"""
Gets existing positions.
@returns: A list with positions. False if there are no positions
"""

def get_positions():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["positions"]) == 0:
            return False
        return config["positions"]
