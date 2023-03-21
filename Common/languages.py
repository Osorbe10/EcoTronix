from Common.constants import CONFIG_FILE, CONFIG_PATH
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
@returns: Default language. False if there are no languages
"""

def get_default_language():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_language in config["languages"]:
            if config_language["default"] == True:
                return config_language["language"]
    return False

"""
Gets language keywords path.
@param language: Language
@returns: Keywords path for language. False if language not exists
"""

def get_kws(language):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_language in config["languages"]:
            if language == config_language["language"]:
                return config_language["kws"]
    return False

"""
Gets default language files path.
@returns: A tuple with language, Hidden Markov Model, dictionary and keywords paths for default language. False if there are no languages
"""

def get_default_language_paths():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_language in config["languages"]:
            if config_language["default"] == True:
                return (config_language["language"], config_language["hmm"], config_language["dic"], config_language["kws"])
    return False

"""
Sets default language.
@param language: Language to set as default
"""

def set_default_language(language):
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_language in config["languages"]:
            if config_language["language"] == language:
                config_language["default"] = True
            elif config_language["default"] == True:
                config_language["default"] = False
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
