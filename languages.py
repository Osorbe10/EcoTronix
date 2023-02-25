from constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, RED
from json import load

"""
Gets language files path.
@param language: Language
@returns: Hidden Markov Model, dictionary and keywords paths for a language. False if language not exists
"""

def get_language_paths(language):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_language in config["languages"]:
            if language == config_language["language"]:
                return (config_language["hmm"], config_language["dic"], config_language["kws"])
    print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing language{DEFAULT}")
    return False

"""
Gets installed languages.
@returns: A list with installed languages. False if there are no languages
"""

def get_installed_languages():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["languages"]) == 0:
            return False
        return [language["language"] for language in config["languages"]]
