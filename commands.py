from constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, GREEN, RED
from json import dump, load
from roles import get_role, role_format

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
Gets a command from config file.
@param command: Command
@returns: Command if is existing. False if not
"""

def get_command(command):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_command in config["commands"]:
            if command.strip() == config_command["command"]:
                return config_command
    return False

"""
Creates a command.
@param command: Command
@param description: Command's description
@param local: True if command is executed locally. False if not. Default is True
@returns: True if the command was created. False if command or description are incomplete or command is existing
"""

def create_command(command, description, local = True):
    if not command_format(command) or not description_format(description):
        return False
    config_command = get_command(command)
    if config_command:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing command{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["commands"].append({"command": command.strip(), "description": description.strip(), "local": local, "roles": []})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Command created{DEFAULT}")
    return True

"""
Removes a command.
@param command: Command
@returns: True if the command was removed. False if command is incomplete or command is not existing
"""

def remove_command(command):
    if not command_format(command):
        return False
    config_command = get_command(command)
    if not config_command:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing command{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["commands"].remove(config_command)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Command removed{DEFAULT}")
    return True

"""
Assigns a command to a role.
@param command: Command
@param role: Role
@returns: True if the command was assigned. False if command or role are incomplete or incorrect or role is already assigned to command
"""

def assign_command(command, role):
    if not command_format(command):
        return False
    if not role_format(role):
        return False
    config_command = get_command(command)
    if not config_command:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing command{DEFAULT}")
        return False
    config_role = get_role(role)
    if not config_role:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing role{DEFAULT}")
        return False
    if config_role["role"] in config_command["roles"]:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Command already assigned to role{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_command in config["commands"]:
            if command.strip() == config_command["command"]:
                config_command["roles"].append(config_role["role"])
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Command assigned to role{DEFAULT}")
    return True

"""
Deassigns a command from a role.
@param command: Command
@param role: Role
@returns: True if the command was deassigned. False if command or role are incomplete or incorrect or role is not assigned to command
"""

def deassign_command(command, role):
    if not command_format(command):
        return False
    if not role_format(role):
        return False
    config_command = get_command(command)
    if not config_command:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing command{DEFAULT}")
        return False
    config_role = get_role(role)
    if not config_role:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing role{DEFAULT}")
        return False
    if config_role["role"] not in config_command["roles"]:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Command not assigned to role{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for config_command in config["commands"]:
            if command.strip() == config_command["command"]:
                config_command["roles"].remove(config_role["role"])
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Command deassigned from role{DEFAULT}")
    return True

"""
Gets existing commands.
@returns: A dictionary with command, description, local or remote and roles for each command. False if there are no commands
"""

def get_commands():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["commands"]) == 0:
            return False
        return [{"command": config_command["command"], "description": config_command["description"], "local": config_command["local"], "roles": config_command["roles"]} for config_command in config["commands"]]
