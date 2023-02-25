from commands import command_format
from constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, GREEN, RED
from json import dump, load
from os import path
from pocketsphinx import get_model_path
from re import compile, findall, sub

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
Gets a estimated threshold of a phrase.
@param phrase: Phrase
@returns: Phrase's estimated threshold. False if phrase is incorrect or has more than 10 syllables
"""

def get_threshold(phrase):
    syllables = get_syllables(phrase)
    threshold = None
    if syllables == 0:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Incorrect phrase{DEFAULT}")
        return False
    elif syllables == 1:
        threshold = 1
    elif syllables == 2:
        threshold = 10
    elif syllables == 3:
        threshold = 15
    elif syllables == 4:
        threshold = 20
    elif syllables == 5:
        threshold = 25
    elif syllables == 6:
        threshold = 30
    elif syllables == 7:
        threshold = 35
    elif syllables == 8:
        threshold = 40
    elif syllables == 9:
        threshold = 45
    elif syllables == 10:
        threshold = 50
    else:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Phrases cannot have more than 10 syllables{DEFAULT}")
        return False
    return threshold

"""
Creates a phrase.
@param language: Language
@param command: Command
@param response: Response
@param phrases: Phrases
@returns: True if the phrase was created. False if command, response or phrases are incomplete or incorrect or command is already configured on this language
"""

def create_phrase(language, command, response, phrases):
    if not command_format(command) or not response_format(response) or not phrases_format(phrases):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_language in config["languages"]:
            if language == config_language["language"]:
                for phrase in config_language["phrases"]:
                    if command == phrase["command"]:
                        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Command already configured in this language{DEFAULT}")
                        return False
                thresholds = []
                new_phrase = {"command": command.strip(), "response": response.strip(), "phrases": []}
                for phrase in compile(r"[\n\r]+").split(phrases.strip().lower()):

                    # TODO: Check if every word exists in that language dictionary file and every phrase is not used for other command. If not, ignore it.

                    threshold = get_threshold(phrase)
                    if not threshold:
                        return False
                    if phrase not in new_phrase["phrases"]:
                        new_phrase["phrases"].append(sub(r"\s+\n", "\n", phrase.strip()).strip())
                        thresholds.append(threshold)
                with open(path.join(get_model_path(), language, config_language["kws"]), "r+") as list_file:
                    lines = list_file.readlines()
                    index = 0
                    for phrase in new_phrase["phrases"]:
                        phrase_with_threshold = phrase + " /1e-" + str(thresholds[index]) + "/\n"
                        if phrase_with_threshold not in lines:
                            lines.append(phrase_with_threshold)
                        index += 1
                    list_file.seek(0)
                    list_file.writelines(sorted(lines))
                config_language["phrases"].append(new_phrase)
                config_file.seek(0)
                dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Phrase created{DEFAULT}")
    return True

"""
Removes a phrase.
@param language: Language
@param command: Command
@returns: True if the phrase was removed. False if command is incomplete or incorrect or is not configured on this language
"""

def remove_phrase(language, command):
    if not command_format(command):
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_language in config["languages"]:
            if language == config_language["language"]:
                for phrase in config_language["phrases"]:
                    if command == phrase["command"]:
                        config_language["phrases"].remove(phrase)
                        config_file.seek(0)
                        dump(config, config_file, indent=4)
                        config_file.truncate()

                        # TODO: Remove phrases from kws file.

                        print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Phrase removed{DEFAULT}")
                        return True
    print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Command not configured in this language{DEFAULT}")
    return False
