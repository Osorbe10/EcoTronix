from Common.constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, GREEN, PICO_PATH, PICO_SETUP_FILE, RED
from Common.positions import get_position, position_format
from Common.rooms import get_room, room_format
from json import dump, load
from subprocess import call

"""
Gets a device from config file.
@param config_room: Room from config file
@param config_position: Position from config file
@returns: Device if is existing. False if not
"""

def get_device(config_room, config_position):
    for config_device in config_room["devices"]:
        if config_position == config_device["position"]:
            return config_device
    return False

"""
Creates a device.
@param room: Room
@param position: Position
@returns: True if the device was created. False if room or position are incomplete or incorrect, room or position are not existing or device is existing in room's position
"""

def create_device(room, position):
    if not room_format(room) or not position_format(position):
        return False
    config_room = get_room(room)
    if not config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing room{DEFAULT}")
        return False
    config_position = get_position(position)
    if not config_position:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing position{DEFAULT}")
        return False
    config_device = get_device(config_room, config_position)
    if config_device:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing device{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_room in config["rooms"]:
            if config_room["room"] == _config_room["room"]:
                _config_room["devices"].append({"position": config_position, "installed": False, "external_peripherals": []})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Device created{DEFAULT}")
    return True

"""
Removes a device.
@param room: Room
@param position: Position
@returns: True if the device was removed. False if room or position are incomplete or incorrect, room or position are not existing or device is not existing in room's position
"""

def remove_device(room, position):
    if not room_format(room) or not position_format(position):
        return False
    config_room = get_room(room)
    if not config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing room{DEFAULT}")
        return False
    config_position = get_position(position)
    if not config_position:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing position{DEFAULT}")
        return False
    config_device = get_device(config_room, config_position)
    if not config_device:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing device{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_room in config["rooms"]:
            if config_room["room"] == _config_room["room"]:
                _config_room["devices"].remove(config_device)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Device removed{DEFAULT}")
    return True

"""
Installs a device.
@param room: Room
@param position: Position
@returns: True if the device was installed. False if room or position are incomplete or incorrect, room or position are not existing, device is not existing in room's position or device is already installed in room's position
"""

def install_device(room, position):
    if not room_format(room) or not position_format(position):
        return False
    config_room = get_room(room)
    if not config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing room{DEFAULT}")
        return False
    config_position = get_position(position)
    if not config_position:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing position{DEFAULT}")
        return False
    config_device = get_device(config_room, config_position)
    if not config_device:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing device{DEFAULT}")
        return False
    if config_device["installed"]:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Device already installed{DEFAULT}")
        return False
    try:
        if call([PICO_PATH + PICO_SETUP_FILE, config_room["room"], config_position]) != 0:
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Device installation failed{DEFAULT}")
            return False
    except KeyboardInterrupt:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Device installation cancelled{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_room in config["rooms"]:
            if config_room["room"] == _config_room["room"]:
                for _config_device in _config_room["devices"]:
                    if config_position == _config_device["position"]:
                        _config_device["installed"] = True
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Device installed{DEFAULT}")
    return True

"""
Gets existing devices.
@returns: A dictionary with room, position, installed or not and external peripherals for each device. False if there are no devices
"""

def get_devices():
    devices = []
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_room in config["rooms"]:
            for config_device in config_room["devices"]:
                devices.append({"room": config_room["room"], "position": config_device["position"], "installed": config_device["installed"], "external_peripherals": config_device["external_peripherals"]})
    if len(devices) == 0:
        return False
    return devices
