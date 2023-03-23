from Common.constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, GREEN, LANGUAGES_PATH, RED
from Common.languages import get_kws_path
from Common.peripherals import peripheral_format
from Common.positions import position_format
from Common.rooms import room_format
from json import dump, load
from os import path
from re import compile, findall, sub

"""
Checks command format.
@param command: Command
@returns: True if command is not empty. False if not
"""

def command_format(command):
    if not command or command.isspace():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Command cannot be empty{DEFAULT}")
        return False
    return True

"""
Checks description format.
@param description: Description
@returns: True if description is not empty. False if not
"""

def description_format(description):
    if not description or description.isspace():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Description cannot be empty{DEFAULT}")
        return False
    return True

"""
Cheecks response format.
@param response: Response
@returns: True if response has correct format. False if not or is empty
"""

def response_format(response):
    if not response or response.isspace():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Response cannot be empty{DEFAULT}")
        return False
    if not all(char.isalpha() or char.isspace() for char in response):
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Response must have only letters and spaces{DEFAULT}")
        return False
    return True

"""
Checks phrases format.
@param phrases: Phrases
@returns: True if phrases have correct format. False if not or are empty
"""

def phrases_format(phrases):
    for phrase in compile(r"[\n\r]+").split(phrases.strip()):
        if not phrase or phrase.isspace():
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Phrases cannot be empty{DEFAULT}")
            return False
        if not all(char.isalpha() or char.isspace() for char in phrase):
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Phrases must have only letters and spaces{DEFAULT}")
            return False
    return True

"""
Gets a local command from config file.
@param command: Local command
@returns: Local command if is existing. False if not
"""

def get_local_command(command):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_command in config["commands"]["local"]:
            if command.strip() == config_command["command"]:
                return config_command
    return False

"""
Gets a remote command from config file.
@param peripheral: Peripheral
@param subtype: Subtype
@param action: Action
@param room: Room
@param position: Position
@returns: Remote command if is existing. False if not
"""

def get_remote_command(peripheral, subtype, action, room, position):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_command in config["commands"]["remote"]:
            if peripheral.strip().lower() == config_command["peripheral"].lower() and subtype.strip().lower() == config_command["subtype"].lower() and action.strip().lower() == config_command["action"].lower() and room.strip().lower() == config_command["room"].lower() and position.strip().lower() == config_command["position"].lower():
                return config_command
    return False

"""
Gets a command from config file.
@param phrase: Phrase
@param language: Language
@returns: Command execution information if is existing. False if not
"""

def get_command(phrase, language):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_command in config["commands"]["local"] + config["commands"]["remote"]:
            for config_phrase in config_command["phrases"]:
                if language == config_phrase["language"] and phrase in config_phrase["phrases"]:
                    del config_command["phrases"]
                    config_command["response"] = config_phrase["response"]
                    return config_command
    return False

"""
Counts the number of syllables in a phrase.
@param phrase: Phrase
@returns: Phrase's number of syllables
"""

def get_syllables(phrase):
    syllables = 0
    for word in findall(r"\w+", phrase.lower()):
        syllables += len(findall(r"[aeiou]", word)) - len(findall(r"[aeiou]{2}", word))
    return syllables

"""
Gets an estimated threshold of a phrase.
@param phrase: Phrase
@returns: Phrase's estimated threshold. False if phrase is incorrect or has more than 10 syllables
"""

def get_threshold(phrase):
    syllables = get_syllables(phrase)
    threshold = False
    if syllables == 0:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Incorrect phrase{DEFAULT}")
    elif syllables == 1:
        threshold = 1
    elif syllables >= 2 and syllables <= 10:
        threshold = syllables * 5
    else:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Phrases cannot have more than 10 syllables{DEFAULT}")
    return threshold

"""
Creates a local command.
@param command: Local command
@param description: Command's description
@param age_restriction: True if command has age_restriction. False if not
@param privileged: True if command is privileged. False if not
@param response: Response
@param phrases: Phrases
@param language: Language
@returns: True if the local command was created. False if local command or description are incomplete or local command is existing
"""

def create_local_command(command, description, age_restriction, privileged, response, phrases, language):
    if not command_format(command) or not description_format(description) or not response_format(response) or not phrases_format(phrases):
        return False
    config_command = get_local_command(command)
    if config_command:
        for phrase in config_command["phrases"]:
            if language == phrase["language"]:
                print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing local command for {language}{DEFAULT}")
                return False
    new_phrase = {"language": language.strip(), "response": response.strip().lower(), "phrases": []}
    thresholds = []
    for phrase in compile(r"[\n\r]+").split(phrases.strip().lower()):

        # TODO: Check if every word exists in that language dictionary file and every phrase is not used for other command. If not, ignore it.
        
        threshold = get_threshold(phrase)
        if not threshold:
            return False
        if phrase not in new_phrase["phrases"]:
            new_phrase["phrases"].append(sub(r"\s+\n", "\n", phrase.strip()).strip())
            thresholds.append(threshold)
    with open(path.join(LANGUAGES_PATH, language, get_kws_path(language)), "r+") as list_file:
        lines = list_file.readlines()
        index = 0
        for phrase in new_phrase["phrases"]:
            phrase_with_threshold = phrase + " /1e-" + str(thresholds[index]) + "/\n"
            if phrase_with_threshold not in lines:
                lines.append(phrase_with_threshold)
            index += 1
        list_file.seek(0)
        list_file.writelines(sorted(lines))
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        if not config_command:
            new_command = {"command": command.strip(), "description": description.strip(), "age_restriction": age_restriction, "privileged": privileged, "phrases": []}
            new_command["phrases"].append(new_phrase)
            config["commands"]["local"].append(new_command)
        else:
            for config_command in config["commands"]["local"]:
                if command == config_command["command"]:
                    config_command["phrases"].append(new_phrase)
                    break
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Local command for {language} created{DEFAULT}")
    return True

"""
Removes a local command.
@param command: Local command
@returns: True if the local command was removed. False if local command is incomplete or local command is not existing
"""

def remove_local_command(command):
    if not command_format(command):
        return False
    config_command = get_local_command(command)
    if not config_command:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing local command{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["commands"]["local"].remove(config_command)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()

    # TODO: Remove phrases from kws file.

    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Local command removed{DEFAULT}")
    return True

"""
Creates a remote command.
@param peripheral: Peripheral
@param subtype: Subtype
@param action: Action
@param room: Room
@param position: Position
@param description: Command's description
@param age_restriction: True if command has age_restriction. False if not
@param privileged: True if command is privileged. False if not
@param response: Response
@param phrases: Phrases
@param language: Language
@returns: True if the remote command was created. False if remote command or description are incomplete or remote command is existing
"""

def create_remote_command(peripheral, subtype, action, room, position, description, age_restriction, privileged, response, phrases, language):
    if not peripheral_format(peripheral) or not room_format(room) or not position_format(position) or not description_format(description) or not response_format(response) or not phrases_format(phrases):
        return False
    config_command = get_remote_command(peripheral, subtype, action, room, position)
    if config_command:
        for phrase in config_command["phrases"]:
            if language == phrase["language"]:
                print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing remote command{DEFAULT}")
                return False
    new_phrase = {"language": language.strip(), "response": response.strip().lower(), "phrases": []}
    thresholds = []
    for phrase in compile(r"[\n\r]+").split(phrases.strip().lower()):

        # TODO: Check if every word exists in that language dictionary file and every phrase is not used for other command. If not, ignore it.
        
        threshold = get_threshold(phrase)
        if not threshold:
            return False
        if phrase not in new_phrase["phrases"]:
            new_phrase["phrases"].append(sub(r"\s+\n", "\n", phrase.strip()).strip())
            thresholds.append(threshold)
    with open(path.join(LANGUAGES_PATH, language, get_kws_path(language)), "r+") as list_file:
        lines = list_file.readlines()
        index = 0
        for phrase in new_phrase["phrases"]:
            phrase_with_threshold = phrase + " /1e-" + str(thresholds[index]) + "/\n"
            if phrase_with_threshold not in lines:
                lines.append(phrase_with_threshold)
            index += 1
        list_file.seek(0)
        list_file.writelines(sorted(lines))
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        if not config_command:
            new_command = {"peripheral": peripheral.strip(), "subtype": subtype.strip(), "action": action.strip(), "room": room.strip(), "position": position.strip(), "description": description.strip(), "age_restriction": age_restriction, "privileged": privileged, "phrases": []}
            new_command["phrases"].append(new_phrase)
            config["commands"]["remote"].append(new_command)
        else:
            for config_command in config["commands"]["remote"]:
                if peripheral == config_command["peripheral"] and subtype == config_command["subtype"] and action == config_command["action"] and room == config_command["room"] and position == config_command["position"]:
                    config_command["phrases"].append(new_phrase)
                    break
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Remote command for {language} created{DEFAULT}")
    return True

"""
Removes a remote command.
@param peripheral: Peripheral
@param subtype: Subtype
@param action: Action
@param room: Room
@param position: Position
@returns: True if the remote command was removed. False if remote command is incomplete or remote command is not existing
"""

def remove_remote_command(peripheral, subtype, action, room, position):
    if not peripheral_format(peripheral) or not room_format(room) or not position_format(position):
        return False
    config_command = get_remote_command(peripheral, subtype, action, room, position)
    if not config_command:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing remote command{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["commands"]["remote"].remove(config_command)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Remote command removed{DEFAULT}")
    return True

"""
Gets existing local commands.
@returns: A dictionary with description, privileged or not and age restriction or not for each local command. False if there are no local commands
"""

def get_local_commands():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["commands"]["local"]) == 0:
            return False
        return [{"description": config_command["description"], "privileged": config_command["privileged"], "age_restriction": config_command["age_restriction"]} for config_command in config["commands"]["local"]]

"""
Gets existing remote commands.
@returns: A dictionary with description, privileged or not and age restriction or not for each remote command. False if there are no remote commands
"""

def get_remote_commands():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["commands"]["remote"]) == 0:
            return False
        return [{"description": config_command["description"], "privileged": config_command["privileged"], "age_restriction": config_command["age_restriction"]} for config_command in config["commands"]["remote"]]
