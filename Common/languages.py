from Common.constants import CONFIG_FILE, CONFIG_PATH, DEFAULT, BLUE, GREEN, RED
from json import dump, load

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

"""
Gets default language.
@returns: Default language
"""

def get_default_language():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        return config["general"]["default_language"]

"""
Gets language keywords path.
@param language: Language
@returns: Keywords path for language. False if language not exists
"""

def get_kws_path(language):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_language in config["languages"]:
            if language == config_language["language"]:
                return config_language["kws"]
    return False

"""
Gets default language files path.
@returns: A tuple with Hidden Markov Model, dictionary and keywords paths for default language. False if there is no default language
"""

def get_default_language_paths():
    default_language = get_default_language()
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_language in config["languages"]:
            if default_language == config_language["language"]:
                return (config_language["hmm"], config_language["dic"], config_language["kws"])
    return False

"""
Sets default language.
@param language: Language to set as default
@returns: True if default language was set. False if language is incomplete or not exists
"""

def set_default_language(language):
    if not language:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Language is incomplete{DEFAULT}")
        return False
    if language not in get_installed_languages():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Language not exists{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["general"]["default_language"] = language
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Default language set{DEFAULT}")
    return True
