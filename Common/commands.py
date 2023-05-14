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
    for word in findall(r"\w+", phrase.strip().lower()):
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
Append new phrases with their estimated thresholds to the kws file.
@param language: Language
@param phrases: Phrases
@param thresholds: Phrase's estimated thresholds
"""

def append_phrases_to_kws_file(language, phrases, thresholds):
    with open(path.join(LANGUAGES_PATH, language, get_kws_path(language)), "r+") as list_file:
        lines = list_file.readlines()
        index = 0
        for phrase in phrases:
            phrase_with_threshold = phrase + " /1e-" + str(thresholds[index]) + "/\n"
            if phrase_with_threshold not in lines:
                lines.append(phrase_with_threshold)
            index += 1
        list_file.seek(0)
        list_file.writelines(sorted(lines))

"""
Removes phrases and their estimated thresholds from the kws file.
@param language: Language
@param phrases: Phrases
"""

def remove_phrases_from_kws_file(language, phrases):
    # TODO: Remove phrases from kws file.
    pass

"""
Manages new phrases.
@param language: Language
@param phrases: Phrases
@param response: Response
@returns: New config phrase if phrases are correct. False if not
"""

def manage_new_phrase(language, phrases, response):
    new_phrase = {"language": language.strip().lower(), "response": response.strip().lower(), "phrases": []}
    thresholds = []
    for phrase in compile(r"[\n\r]+").split(phrases.strip().lower()):
        # TODO: Check if every word exists in that language dictionary file and every phrase is not used for other command. If not, ignore it.
        threshold = get_threshold(phrase)
        if not threshold:
            return False
        if phrase not in new_phrase["phrases"]:
            new_phrase["phrases"].append(sub(r"\s+\n", "\n", phrase.strip()).strip())
            thresholds.append(threshold)
    append_phrases_to_kws_file(language, new_phrase["phrases"], thresholds)
    return new_phrase

"""
Creates a local command.
@param command: Local command
@param description: Command's description
@param age_restriction: True if command has age_restriction. False if not
@param privileged: True if command is privileged. False if not
@param response: Response
@param phrases: Phrases
@param language: Language
@returns: True if the local command was created. False if local command is incomplete or description, response and phrases are incomplete or incorrect or local command is existing
"""

def create_local_command(command, description, age_restriction, privileged, response, phrases, language):
    if not command_format(command) or not description_format(description) or not response_format(response) or not phrases_format(phrases):
        return False
    config_command = get_local_command(command)
    if config_command:
        for phrase in config_command["phrases"]:
            if language.strip().lower() == phrase["language"]:
                print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing local command for {language}{DEFAULT}")
                return False
    new_phrase = manage_new_phrase(language, phrases, response)
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        if not config_command:
            new_command = {"command": command.strip(), "description": description.strip(), "age_restriction": age_restriction, "privileged": privileged, "phrases": []}
            new_command["phrases"].append(new_phrase)
            config["commands"]["local"].append(new_command)
        else:
            for config_command in config["commands"]["local"]:
                if command.strip() == config_command["command"]:
                    config_command["phrases"].append(new_phrase)
                    break
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Local command for {language} created{DEFAULT}")
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
@returns: True if the remote command was created. False if remote command, description, response or phrases are incomplete or incorrect or remote command is existing
"""

def create_remote_command(peripheral, subtype, action, room, position, description, age_restriction, privileged, response, phrases, language):
    if not peripheral_format(peripheral) or not room_format(room) or not position_format(position) or not description_format(description) or not response_format(response) or not phrases_format(phrases):
        return False
    config_command = get_remote_command(peripheral, subtype, action, room, position)
    if config_command:
        for phrase in config_command["phrases"]:
            if language.strip().lower() == phrase["language"]:
                print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing remote command{DEFAULT}")
                return False
    new_phrase = manage_new_phrase(language, phrases, response)
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        if not config_command:
            new_command = {"peripheral": peripheral.strip(), "subtype": subtype.strip(), "action": action.strip(), "room": room.strip(), "position": position.strip(), "description": description.strip(), "age_restriction": age_restriction, "privileged": privileged, "phrases": []}
            new_command["phrases"].append(new_phrase)
            config["commands"]["remote"].append(new_command)
        else:
            for config_command in config["commands"]["remote"]:
                if peripheral.strip() == config_command["peripheral"] and subtype.strip() == config_command["subtype"] and action.strip() == config_command["action"] and room.strip() == config_command["room"] and position.strip() == config_command["position"]:
                    config_command["phrases"].append(new_phrase)
                    break
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Remote command for {language} created{DEFAULT}")
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
    #remove_phrases_from_kws_file(language, phrases) for all languages
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Local command removed{DEFAULT}")
    return True

"""
Removes a remote command.
@param peripheral: Peripheral
@param subtype: Subtype
@param action: Action
@param room: Room
@param position: Position
@returns: True if the remote command was removed. False if remote command is incomplete or incorrect or remote command is not existing
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
    #remove_phrases_from_kws_file(language, phrases) for all languages
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Remote command removed{DEFAULT}")
    return True

"""
Gets existing local commands.
@returns: A dictionary with command, description, privileged or not and age restriction or not for each local command. False if there are no local commands
"""

def get_local_commands():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["commands"]["local"]) == 0:
            return False
        return [{"command": config_command["command"], "description": config_command["description"], "privileged": config_command["privileged"], "age_restriction": config_command["age_restriction"]} for config_command in config["commands"]["local"]]

"""
Gets existing remote commands.
@returns: A dictionary with room, position, peripheral, subtype, action, description, privileged or not and age restriction or not for each remote command. False if there are no remote commands
"""

def get_remote_commands():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["commands"]["remote"]) == 0:
            return False
        return [{"room": config_command["room"], "position": config_command["position"], "peripheral": config_command["peripheral"], "subtype": config_command["subtype"], "action": config_command["action"], "description": config_command["description"], "privileged": config_command["privileged"], "age_restriction": config_command["age_restriction"]} for config_command in config["commands"]["remote"]]

"""
Edits a local command.
@param old_command: Old local command
@param new_command: New local command
@param new_description: New command's description
@param new_age_restriction: True if command has age_restriction. False if not
@param new_privileged: True if command is privileged. False if not
@param new_response: New response
@param new_phrases: New phrases
@param new_language: New language
@returns: True if the local command was edited. False if both commands are incomplete or description, response or phrases are incomplete or incorrect or old command is not existing or new command is existing or command has no changes
"""

def edit_local_command(old_command, new_command, new_description, new_age_restriction, new_privileged, new_response, new_phrases, new_language):
    if not command_format(old_command) or not command_format(new_command) or not description_format(new_description) or not response_format(new_response) or not phrases_format(new_phrases):
        return False
    config_command = get_local_command(new_command)
    if config_command and old_command.strip().lower() != new_command.strip().lower():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing new local command{DEFAULT}")
        return False
    config_command = get_local_command(old_command)
    if not config_command:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing old local command{DEFAULT}")
        return False
    if config_command["command"] == new_command.strip() and config_command["description"] == new_description.strip() and config_command["age_restriction"] == new_age_restriction and config_command["privileged"] == new_privileged:
        for config_phrase in config_command["phrases"]:
            if new_language.strip().lower() == config_phrase["language"]:
                if config_phrase["response"] == new_response.strip():
                    same_phrases = True
                    for phrase in compile(r"[\n\r]+").split(new_phrases.strip().lower()):
                        if phrase not in config_phrase["phrases"]:
                            same_phrases = False
                            break
                    if same_phrases:
                        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Local command has no changes{DEFAULT}")
                        return False
                break
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_command in config["commands"]["local"]:
            if config_command["command"] == _config_command["command"]:
                _config_command["command"] = new_command.strip()
                _config_command["description"] = new_description.strip()
                _config_command["age_restriction"] = new_age_restriction
                _config_command["privileged"] = new_privileged
                new_phrase = manage_new_phrase(new_language, new_phrases, new_response)
                is_new_language = True
                for _config_phrase in _config_command["phrases"]:
                    if new_language.strip().lower() == _config_phrase["language"]:
                        _config_phrase["response"] = new_phrase["response"]
                        _config_phrase["phrases"] = new_phrase["phrases"]
                        is_new_language = False
                        break
                if is_new_language:
                    _config_command["phrases"].append(new_phrase)
                break
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Local command edited{DEFAULT}")
    return True

"""
Edits a remote command.
@param old_peripheral: Old peripheral
@param old_subtype: Old subtype
@param old_action: Old action
@param old_room: Old room
@param old_position: Old position
@param new_peripheral: New peripheral
@param new_subtype: New subtype
@param new_action: New action
@param new_room: New room
@param new_position: New position
@param new_description: New command's description
@param new_age_restriction: True if command has age_restriction. False if not
@param new_privileged: True if command is privileged. False if not
@param new_response: New response
@param new_phrases: New phrases
@param new_language: New language
@returns: True if the remote command was edited. False if both commands are incomplete or description, response or phrases are incomplete or incorrect or old command is not existing or new command is existing or command has no changes
"""

def edit_remote_command(old_peripheral, old_subtype, old_action, old_room, old_position, new_peripheral, new_subtype, new_action, new_room, new_position, new_description, new_age_restriction, new_privileged, new_response, new_phrases, new_language):
    if not peripheral_format(old_peripheral) or not room_format(old_room) or not position_format(old_position) or not peripheral_format(new_peripheral) or not room_format(new_room) or not position_format(new_position) or not description_format(new_description) or not response_format(new_response) or not phrases_format(new_phrases):
        return False
    config_command = get_remote_command(new_peripheral, new_subtype, new_action, new_room, new_position)
    if config_command and (old_peripheral.strip().lower() != new_peripheral.strip().lower() or old_subtype.strip().lower() != new_subtype.strip().lower() or old_action.strip().lower() != new_action.strip().lower() or old_room.strip().lower() != new_room.strip().lower() or old_position.strip().lower() != new_position.strip().lower()):
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing new remote command{DEFAULT}")
        return False
    config_command = get_remote_command(old_peripheral, old_subtype, old_action, old_room, old_position)
    if not config_command:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing old remote command{DEFAULT}")
        return False
    if config_command["peripheral"] == new_peripheral.strip() and config_command["subtype"] == new_subtype.strip() and config_command["action"] == new_action.strip() and config_command["room"] == new_room.strip() and config_command["position"] == new_position.strip() and config_command["description"] == new_description.strip() and config_command["age_restriction"] == new_age_restriction and config_command["privileged"] == new_privileged:
        for config_phrase in config_command["phrases"]:
            if new_language.strip().lower() == config_phrase["language"]:
                if config_phrase["response"] == new_response.strip():
                    same_phrases = True
                    for phrase in compile(r"[\n\r]+").split(new_phrases.strip().lower()):
                        if phrase not in config_phrase["phrases"]:
                            same_phrases = False
                            break
                    if same_phrases:
                        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Remote command has no changes{DEFAULT}")
                        return False
                break
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_command in config["commands"]["remote"]:
            if config_command["peripheral"] == _config_command["peripheral"] and config_command["subtype"] == _config_command["subtype"] and config_command["action"] == _config_command["action"] and config_command["room"] == _config_command["room"] and config_command["position"] == _config_command["position"]:
                _config_command["peripheral"] = new_peripheral.strip()
                _config_command["subtype"] = new_subtype.strip()
                _config_command["action"] = new_action.strip()
                _config_command["room"] = new_room.strip()
                _config_command["position"] = new_position.strip()
                _config_command["description"] = new_description.strip()
                _config_command["age_restriction"] = new_age_restriction
                _config_command["privileged"] = new_privileged
                new_phrase = manage_new_phrase(new_language, new_phrases, new_response)
                is_new_language = True
                for _config_phrase in _config_command["phrases"]:
                    if new_language.strip().lower() == _config_phrase["language"]:
                        _config_phrase["response"] = new_phrase["response"]
                        _config_phrase["phrases"] = new_phrase["phrases"]
                        is_new_language = False
                        break
                if is_new_language:
                    _config_command["phrases"].append(new_phrase)
                break
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Remote command edited{DEFAULT}")
    return True
