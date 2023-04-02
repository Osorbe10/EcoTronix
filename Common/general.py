from Common.constants import CONFIG_FILE, CONFIG_PATH, DEFAULT, BLUE, GREEN, PICO_CONFIG_TEMPLATE_FILE, PICO_PATH, RED
from json import dump, load

"""
Gets legal age.
@returns: Legal age
"""

def get_legal_age():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        return config["general"]["legal_age"]
    
"""
Sets legal age.
@param legal_age: Legal age
@returns: True if legal age was set. False if legal age is incomplete or incorrect
"""

def set_legal_age(legal_age):
    if not legal_age:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Legal age is incomplete{DEFAULT}")
        return False
    if not legal_age.isdigit():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Legal age is incorrect{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["general"]["legal_age"] = int(legal_age)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Legal age set{DEFAULT}")
    return True

"""
Gets wifi password.
@returns: Wifi password
"""

def get_wifi_password():
    with open(PICO_PATH + PICO_CONFIG_TEMPLATE_FILE, "r") as pico_config_file:
        config = load(pico_config_file)
        return config["wifi"]["password"]

"""
Gets wifi SSID.
@returns: Wifi SSID
"""

def get_wifi_ssid():
    with open(PICO_PATH + PICO_CONFIG_TEMPLATE_FILE, "r") as pico_config_file:
        config = load(pico_config_file)
        return config["wifi"]["ssid"]

"""
Sets wifi credentials.
@param wifi_ssid: Wifi SSID
@param wifi_password: Wifi password
"""

def set_wifi_credentials(wifi_ssid, wifi_password):
    if not wifi_ssid:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Wifi SSID is incomplete{DEFAULT}")
        return False
    if not wifi_password:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Wifi password is incomplete{DEFAULT}")
        return False
    with open(PICO_PATH + PICO_CONFIG_TEMPLATE_FILE, "r+") as pico_config_file:
        config = load(pico_config_file)
        config["wifi"]["ssid"] = wifi_ssid
        config["wifi"]["password"] = wifi_password
        pico_config_file.seek(0)
        dump(config, pico_config_file, indent=4)
        pico_config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Wifi credentials set{DEFAULT}")
    return True
