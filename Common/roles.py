from Common.constants import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, GREEN, RED
from Common.users import age, get_user, name_format
from json import dump, load

"""
Checks role format.
@param role: Role
@returns: True if role has correct format. False if not or is empty
"""

def role_format(role):
    if not role or role.isspace():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role cannot be empty{DEFAULT}")
        return False
    if not all(char.isalpha() or char.isspace() for char in role):
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role must have only letters and spaces{DEFAULT}")
        return False
    return True

"""
Gets a role from config file.
@param role: Role
@returns: Role if is existing. False if not
"""

def get_role(role):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        for config_role in config["roles"]:
            if role.strip().lower() == config_role["role"].lower():
                return config_role
    return False

"""
Creates a role.
@param role: Role
@param age_restriction: True if role has age restriction. False if not
@param privileged: True if role is privileged. False if not
@returns: True if the role was created. False if role is incomplete or incorrect or role is existing
"""

def create_role(role, age_restriction, privileged):
    if not role_format(role):
        return False
    config_role = get_role(role)
    if config_role:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing role{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["roles"].append({"role": role.strip().capitalize(), "age_restriction": age_restriction, "privileged": privileged, "users": []})
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Role created{DEFAULT}")
    return True

"""
Edits a role.
@param old_role: Old role
@param new_role: New role
@param new_age_restriction: True if role has age restriction. False if not
@param new_privileged: True if role is privileged. False if not
@returns: True if the role was edited. False if both roles are incomplete or incorrect or old role is not existing or new role is existing or role has no changes
"""

def edit_role(old_role, new_role, new_age_restriction, new_privileged):
    if not role_format(old_role) or not role_format(new_role):
        return False
    config_role = get_role(new_role)
    if config_role and old_role.strip().lower() != new_role.strip().lower():
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Existing new role{DEFAULT}")
        return False
    config_role = get_role(old_role)
    if not config_role:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing old role{DEFAULT}")
        return False
    if config_role["role"] == new_role.strip().capitalize() and config_role["age_restriction"] == new_age_restriction and config_role["privileged"] == new_privileged:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role has no changes{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_role in config["roles"]:
            if config_role["role"] == _config_role["role"]:
                _config_role["role"] = new_role.strip().capitalize()
                _config_role["age_restriction"] = new_age_restriction
                _config_role["privileged"] = new_privileged
                break
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Role edited{DEFAULT}")
    return True

"""
Removes a role.
@param role: Role
@returns: True if the role was removed. False if role is incomplete or incorrect or role is not existing
"""

def remove_role(role):
    if not role_format(role):
        return False
    config_role = get_role(role)
    if not config_role:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing role{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        config["roles"].remove(config_role)
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Role removed{DEFAULT}")
    return True

"""
Assigns a role to a user.
@param role: Role
@param name: User name
@returns: True if the role was assigned. False if role or user are incomplete or incorrect, role has age restriction and user is of legal age or user is already assigned to role
"""

def assign_role(role, name):
    if not role_format(role) or not name_format(name):
        return False
    config_role = get_role(role)
    if not config_role:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing role{DEFAULT}")
        return False
    config_user = get_user(name)
    if not config_user:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing user{DEFAULT}")
        return False
    if config_user["name"] in config_role["users"]:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role already assigned to user{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        if config_role["age_restriction"] and age(config_user["birth_date"]) >= config["general"]["legal_age"]:
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}User is of legal age{DEFAULT}")
            return False
        for _config_role in config["roles"]:
            if config_role["role"] == _config_role["role"]:
                _config_role["users"].append(config_user["name"])
        config_file.seek(0)
        dump(config, config_file, indent=4)
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Role assigned to user{DEFAULT}")
    return True

"""
Deassigns a role from a user.
@param role: Role
@param user: User name
@returns: True if the role was deassigned. False if role or user are incomplete or incorrect or user is not assigned to role
"""

def deassign_role(role, name):
    if not role_format(role) or not name_format(name):
        return False
    config_role = get_role(role)
    if not config_role:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing role{DEFAULT}")
        return False
    config_user = get_user(name)
    if not config_user:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing user{DEFAULT}")
        return False
    if config_user["name"] not in config_role["users"]:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Role not assigned to user{DEFAULT}")
        return False
    with open(CONFIG_PATH + CONFIG_FILE, "r+") as config_file:
        config = load(config_file)
        for _config_role in config["roles"]:
            if config_role["role"] == _config_role["role"]:
                _config_role["users"].remove(config_user["name"])
        config_file.seek(0)
        dump(config, config_file, indent=4)
        config_file.truncate()
    print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Role deassigned from user{DEFAULT}")
    return True

"""
Gets existing roles.
@returns: A dictionary with role, age restriction, privileged and users for each role. False if there are no roles
"""

def get_roles():
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = load(config_file)
        if len(config["roles"]) == 0:
            return False
        return [{"role": config_role["role"], "age_restriction": config_role["age_restriction"], "privileged": config_role["privileged"], "users": config_role["users"]} for config_role in config["roles"]]
