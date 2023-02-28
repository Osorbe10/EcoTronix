from constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, GREEN, PICO_PATH, PICO_SETUP, POSITIONS_IN_ROOM, RED
from json import dump, load
from rooms import get_room, room_format
from subprocess import call

"""
Gets a device from config file.
@param config_room: Room from config file
@param position: Device's position in the room
@returns: Device if is existing. False if not
"""

def get_device(config_room, position):
    for config_device in config_room["devices"]:
        if position == config_device["position"]:
            return config_device
    return False

"""
Creates a device.
@param room: Room
@param position: Device's position in the room
@returns: True if the device was created. False if room or position are incomplete or incorrect, room is not existing or device is existing in room's position
"""

def create_device(room, position):
    if not room_format(room):
        return False
    if not position or position not in POSITIONS_IN_ROOM:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Position not valid{DEFAULT}")
        return False
    config_room = get_room(room)
    if not config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing room{DEFAULT}")
        return False
    config_device = get_device(config_room, position)
    if config_device:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing device in room's position{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_room in config["rooms"]:
            if room.strip() == config_room["room"]:
                config_room["devices"].append({"position": position, "installed": False, "peripherals": []})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Device assigned to room{DEFAULT}")
    return True

"""
Removes a device.
@param room: Room
@param position: Device's position in the room
@returns: True if the device was removed. False if room or position are incomplete or incorrect, room is not existing or device is not existing in room's position
"""

def remove_device(room, position):
    if not room_format(room):
        return False
    if not position or position not in POSITIONS_IN_ROOM:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Position not valid{DEFAULT}")
        return False
    config_room = get_room(room)
    if not config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing room{DEFAULT}")
        return False
    config_device = get_device(config_room, position)
    if not config_device:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing device in room's position{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_room in config["rooms"]:
            if room.strip() == config_room["room"]:
                config_room["devices"].remove(config_device)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Device removed from room{DEFAULT}")
    return True

"""
Installs a device.
@param room: Room
@param position: Device's position in the room
@returns: True if the device was installed. False if room or position are incomplete or incorrect, room is not existing, device is not existing in room's position or device is already installed in room's position
"""

def install_device(room, position):
    if not room_format(room):
        return False
    if not position or position not in POSITIONS_IN_ROOM:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Position not valid{DEFAULT}")
        return False
    config_room = get_room(room)
    if not config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing room{DEFAULT}")
        return False
    config_device = get_device(config_room, position)
    if not config_device:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing device in room's position{DEFAULT}")
        return False
    if config_device["installed"]:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Device already installed{DEFAULT}")
        return False
    try:
        if call([PICO_PATH + PICO_SETUP, room, position]) != 0:
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Device installation failed{DEFAULT}")
            return False
    except KeyboardInterrupt:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Device installation cancelled{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_room in config["rooms"]:
            if room.strip() == config_room["room"]:
                for config_device in config_room["devices"]:
                    if position == config_device["position"]:
                        config_device["installed"] = True
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Device installed{DEFAULT}")
    return True
