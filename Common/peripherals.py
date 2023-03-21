from Common.constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, GREEN, PERIPHERALS_FILE, PICO_PATH, RED
from Common.devices import get_device
from Common.positions import position_format
from Common.rooms import get_room, room_format
from json import dump, load

"""
Checks peripheral format.
@param peripheral: Peripheral
@returns: True if peripheral has correct format. False if not or is empty
"""

def peripheral_format(peripheral):
    if not peripheral or peripheral.isspace():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Peripheral cannot be empty{DEFAULT}")
        return False
    if not all(char.isalpha() or char.isspace() for char in peripheral):
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Peripheral must have only letters and spaces{DEFAULT}")
        return False
    return True

"""
Gets an external peripheral from config file.
@param peripheral: External peripheral
@returns: External peripheral if is existing. False if not
"""

def get_external_peripheral(peripheral):
    with open(PICO_PATH + PERIPHERALS_FILE, "r") as config_file:
        config = load(config_file)
        for config_peripheral in config["external"]:
            if peripheral.strip() == config_peripheral["type"]:
                return config_peripheral
    return False

"""
Assigns an external peripheral to a device.
@param peripheral: External peripheral
@param room: Room
@param position: Position
@returns: True if the external peripheral was assigned. False if external peripheral or device are incomplete or external peripheral is already assigned to device
"""

def assign_external_peripheral(peripheral, room, position):
    if not peripheral_format(peripheral) or not room_format(room) or not position_format(position):
        return False
    config_peripheral = get_external_peripheral(peripheral)
    if not config_peripheral:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing peripheral{DEFAULT}")
        return False
    config_device = get_device(get_room(room), position)
    if not config_device:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing device{DEFAULT}")
        return False
    if config_peripheral["type"] in config_device["external_peripherals"]:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Peripheral already assigned to device{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_room in config["rooms"]:
            if room.strip() == config_room["room"]:
                for config_device in config_room["devices"]:
                    if position.strip() == config_device["position"]:
                        config_device["external_peripherals"].append(config_peripheral["type"])
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Peripheral assigned to device{DEFAULT}")
    return True

"""
Deassigns an external peripheral from a device.
@param peripheral: External peripheral
@param room: Room
@param position: Position
@returns: True if the external peripheral was deassigned. False if external peripheral or device are incomplete or external peripheral is not assigned to device
"""

def deassign_external_peripheral(peripheral, room, position):
    if not peripheral_format(peripheral) or not room_format(room) or not position_format(position):
        return False
    config_peripheral = get_external_peripheral(peripheral)
    if not config_peripheral:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing peripheral{DEFAULT}")
        return False
    config_device = get_device(get_room(room), position)
    if not config_device:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing device{DEFAULT}")
        return False
    if config_peripheral["type"] not in config_device["external_peripherals"]:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Peripheral not assigned to device{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_room in config["rooms"]:
            if room.strip() == config_room["room"]:
                for config_device in config_room["devices"]:
                    if position.strip() == config_device["position"]:
                        config_device["external_peripherals"].remove(config_peripheral["type"])
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Peripheral deassigned from device{DEFAULT}")
    return True

"""
Gets existing internal peripherals.
@returns: A list with internal peripherals. False if there are no internal peripherals
"""

def get_internal_peripherals():
    with open(PICO_PATH + PERIPHERALS_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["internal"]) == 0:
            return False
        return [{"type": config_peripheral["type"], "sensor": config_peripheral["sensor"], "actuator": config_peripheral["actuator"]} for config_peripheral in config["internal"]]

"""
Gets existing external peripherals.
@returns: A list with external peripherals. False if there are no external peripherals
"""

def get_external_peripherals():
    with open(PICO_PATH + PERIPHERALS_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["external"]) == 0:
            return False
        return [{"type": config_peripheral["type"], "sensor": config_peripheral["sensor"], "actuator": config_peripheral["actuator"]} for config_peripheral in config["external"]]

"""
Gets device peripherals.
@param room: Room
@param position: Position
@returns: A list with device peripherals. False if room or position are incomplete or incorrect, room is not existing, device is not existing in room's position or device is not installed in room's position
"""

def get_device_peripherals(room, position):
    if not room_format(room) or not position_format(position):
        return False
    config_room = get_room(room)
    if not config_room:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing room{DEFAULT}")
        return False
    config_device = get_device(config_room, position)
    if not config_device:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing device in room's position{DEFAULT}")
        return False
    return config_device["external_peripherals"] + [peripheral["type"] for peripheral in get_internal_peripherals()]

"""
Gets peripheral actions.
@param peripheral: Peripheral
@returns: A list with peripheral actions. False if peripheral is incomplete or incorrect, peripheral is not existing or peripheral has no actions
"""

def get_peripheral_actions(peripheral):
    if not peripheral_format(peripheral):
        return False
    with open(PICO_PATH + PERIPHERALS_FILE, "r") as config_file:
        config = load(config_file)
        for config_peripheral in config["external"] + config["internal"]:
            if peripheral.strip() == config_peripheral["type"]:
                if "actions" in config_peripheral:
                    return config_peripheral["actions"]
                break
    return False

"""
Gets peripheral subtypes.
@param peripheral: Peripheral
@returns: A list with peripheral subtypes. False if peripheral is incomplete or incorrect, peripheral is not existing or peripheral has no subtypes
"""

def get_peripheral_subtypes(peripheral):
    if not peripheral_format(peripheral):
        return False
    with open(PICO_PATH + PERIPHERALS_FILE, "r") as config_file:
        config = load(config_file)
        for config_peripheral in config["external"] + config["internal"]:
            if peripheral.strip() == config_peripheral["type"]:
                if "subtypes" in config_peripheral:
                    return [config_subtype["subtype"] for config_subtype in config_peripheral["subtypes"]]
                break
    return False
