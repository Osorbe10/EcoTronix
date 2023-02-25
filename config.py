#!/usr/bin/env python3

from commands import create_command, get_commands, remove_command, assign_command, deassign_command
from constants import BLUE, DEFAULT, POSITIONS_IN_ROOM, RED, YELLOW
from devices import create_device, install_device, remove_device
from languages import get_installed_languages
from os import getuid
from phrases import create_phrase, remove_phrase
from roles import create_role, get_roles, remove_role, assign_role, deassign_role
from rooms import create_room, get_rooms, remove_room
from users import create_user, get_users, remove_user
from tkinter import ALL, BooleanVar, BOTH, Button, Canvas, Checkbutton, END, Entry, Frame, Label, LabelFrame, LEFT, Listbox, N, OptionMenu, Radiobutton, RIGHT, Scrollbar, StringVar, Text, Tk, TOP, VERTICAL, W, Y

"""
Creates a room in graphical mode.
"""

def gui_create_room():
    room = rooms_room_entry.get()
    create_room(room)
    gui_update_devices_room_menu()
    gui_update_rooms_devices_list()

"""
Removes a room in graphical mode.
"""

def gui_remove_room():
    room = rooms_room_entry.get()
    remove_room(room)
    gui_update_devices_room_menu()
    gui_update_rooms_devices_list()

"""
Update rooms menu in graphical mode.
"""

def gui_update_devices_room_menu():
    devices_room_menu["menu"].delete(0, END)
    rooms = get_rooms()
    if rooms:
        for room in rooms:
            devices_room_menu["menu"].add_command(label=room["room"], command=lambda value=room["room"]: devices_room_entry.set(value))
        devices_room_entry.set(rooms[0]["room"])
    else:
        devices_room_menu["menu"].add_command(label="", command=lambda value="": devices_room_entry.set(value))
        devices_room_entry.set("")

"""
Update room's and device's list in graphical mode.
"""

def gui_update_rooms_devices_list():
    rooms_devices_list.delete(0, END)
    rooms = get_rooms()
    if rooms:
        for room in rooms:
            rooms_devices_list.insert(END, room["room"] + " [ " + ", ".join([device["position"] if device["installed"] else device["position"] + " (not installed)" for device in room["devices"]]) + " ]")
    else:
        rooms_devices_list.insert(END, "Non existing rooms...")
    rooms_devices_list.config(width=max([len(room) for room in rooms_devices_list.get(0, END)]))
    rooms_devices_list.config(height=rooms_devices_list.size())

"""
Creates a device in graphical mode.
"""

def gui_create_device():
    room = devices_room_entry.get()
    position = devices_position_entry.get()
    create_device(room, position)
    gui_update_rooms_devices_list()

"""
Removes a device in graphical mode.
"""

def gui_remove_device():
    room = devices_room_entry.get()
    position = devices_position_entry.get()
    remove_device(room, position)
    gui_update_rooms_devices_list()

"""
Installs a device in graphical mode.
"""

def gui_install_device():
    room = devices_room_entry.get()
    position = devices_position_entry.get()
    install_device(room, position)
    gui_update_rooms_devices_list()

"""
Creates a user in graphical mode.
"""

def gui_create_user():
    name = users_name_entry.get()
    birth_date = users_birth_date_entry.get()
    language = users_language_entry.get()
    create_user(name, birth_date, language)
    gui_update_roles_users_user_menu()
    gui_update_users_list()

"""
Removes a user in graphical mode.
"""

def gui_remove_user():
    name = users_name_entry.get()
    remove_user(name)
    gui_update_roles_users_user_menu()
    gui_update_users_list()
    gui_update_roles_list()

"""
Update role's user assignation menu in graphical mode.
"""

def gui_update_roles_users_user_menu():
    roles_users_user_menu["menu"].delete(0, END)
    users = get_users()
    if users:
        for user in users:
            roles_users_user_menu["menu"].add_command(label=user["name"], command=lambda value=user["name"]: roles_users_user_entry.set(value))
        roles_users_user_entry.set(users[0]["name"])
    else:
        roles_users_user_menu["menu"].add_command(label="", command=lambda value="": roles_users_user_entry.set(value))
        roles_users_user_entry.set("")

"""
Update user's list in graphical mode.
"""

def gui_update_users_list():
    users_list.delete(0, END)
    users = get_users()
    if users:
        for user in users:
            users_list.insert(END, user["name"] + " [ " + str(user["age"]) + " years ] [ " + user["language"] + " ]")
    else:
        users_list.insert(END, "Non existing users...")
    users_list.config(width=max([len(user) for user in users_list.get(0, END)]))
    users_list.config(height=users_list.size())

"""
Creates a role in graphical mode.
"""

def gui_create_role():
    role = roles_role_entry.get()
    age_restriction = roles_age_restriction_entry.get()
    create_role(role, age_restriction)
    gui_update_roles_users_role_menu()
    gui_update_commands_roles_role_menu()
    gui_update_roles_list()

"""
Removes a role in graphical mode.
"""

def gui_remove_role():
    role = roles_role_entry.get()
    remove_role(role)
    gui_update_roles_users_role_menu()
    gui_update_commands_roles_role_menu()
    gui_update_roles_list()
    gui_update_command_list()

"""
Update roles's role assignation menu in graphical mode.
"""

def gui_update_roles_users_role_menu():
    roles_users_role_menu["menu"].delete(0, END)
    roles = get_roles()
    if roles:
        for role in roles:
            roles_users_role_menu["menu"].add_command(label=role["role"], command=lambda value=role["role"]: roles_users_role_entry.set(value))
        roles_users_role_entry.set(roles[0]["role"])
    else:
        roles_users_role_menu["menu"].add_command(label="", command=lambda value="": roles_users_role_entry.set(value))
        roles_users_role_entry.set("")

"""
Update role's list in graphical mode.
"""

def gui_update_roles_list():
    roles_list.delete(0, END)
    roles = get_roles()
    if roles:
        for role in roles:
            roles_list.insert(END, role["role"] + " [ age restriction: " + str(role["age_restriction"]) + " ] [ " + ", ".join(role["users"]) + " ]")
    else:
        roles_list.insert(END, "Non existing roles...")
    roles_list.config(width=max([len(role) for role in roles_list.get(0, END)]))
    roles_list.config(height=roles_list.size())

"""
Assign a role to a user in graphical mode.
"""

def gui_assign_role():
    role = roles_users_role_entry.get()
    user = roles_users_user_entry.get()
    assign_role(role, user)
    gui_update_roles_list()

"""
Deassign a role from a user in graphical mode.
"""

def gui_deassign_role():
    role = roles_users_role_entry.get()
    user = roles_users_user_entry.get()
    deassign_role(role, user)
    gui_update_roles_list()

"""
Creates a command in graphical mode.
"""

def gui_create_command():
    command = commands_command_entry.get()
    description = commands_description_entry.get()
    local = commands_local_entry.get()
    create_command(command, description, local)
    gui_update_commands_roles_command_menu()
    gui_update_phrases_command_menu()
    gui_update_command_list()

"""
Removes a command in graphical mode.
"""

def gui_remove_command():
    command = commands_command_entry.get()
    remove_command(command)
    gui_update_commands_roles_command_menu()
    gui_update_phrases_command_menu()
    gui_update_command_list()

"""
Update commands's command assignation menu in graphical mode.
"""

def gui_update_commands_roles_command_menu():
    commands_roles_command_menu["menu"].delete(0, END)
    commands = get_commands()
    if commands:
        for command in commands:
            commands_roles_command_menu["menu"].add_command(label=command["description"], command=lambda value=command["command"]: commands_roles_command_entry.set(value))
        commands_roles_command_entry.set(commands[0]["command"])
    else:
        commands_roles_command_menu["menu"].add_command(label="", command=lambda value="": commands_roles_command_entry.set(value))
        commands_roles_command_entry.set("")

"""
Update commands's role assignation menu in graphical mode.
"""

def gui_update_commands_roles_role_menu():
    commands_roles_role_menu["menu"].delete(0, END)
    roles = get_roles()
    if roles:
        for role in roles:
            commands_roles_role_menu["menu"].add_command(label=role["role"], command=lambda value=role["role"]: commands_roles_role_entry.set(value))
        commands_roles_role_entry.set(roles[0]["role"])
    else:
        commands_roles_role_menu["menu"].add_command(label="", command=lambda value="": commands_roles_role_entry.set(value))
        commands_roles_role_entry.set("")

"""
Update phrases's command menu in graphical mode.
"""

def gui_update_phrases_command_menu():
    phrases_command_menu["menu"].delete(0, END)
    commands = get_commands()
    if commands:
        for command in commands:
            phrases_command_menu["menu"].add_command(label=command["description"], command=lambda value=command["command"]: phrases_command_entry.set(value))
        phrases_command_entry.set(commands[0]["command"])
    else:
        phrases_command_menu["menu"].add_command(label="", command=lambda value="": phrases_command_entry.set(value))
        phrases_command_entry.set("")

"""
Update command's list in graphical mode.
"""

def gui_update_command_list():
    commands_list.delete(0, END)
    commands = get_commands()
    if commands:
        for command in commands:
            commands_list.insert(END, command["description"] + " [ local: " + str(command["local"]) + " ] [ " + ", ".join(command["roles"]) + " ]")
    else:
        commands_list.insert(END, "Non existing commands...")
    commands_list.config(width=max([len(command) for command in commands_list.get(0, END)]))
    commands_list.config(height=commands_list.size())

"""
Assign a command to a role in graphical mode.
"""

def gui_assign_command():
    command = commands_roles_command_entry.get()
    role = commands_roles_role_entry.get()
    assign_command(command, role)
    gui_update_command_list()

"""
Deassign a command from a role in graphical mode.
"""

def gui_deassign_command():
    command = commands_roles_command_entry.get()
    role = commands_roles_role_entry.get()
    deassign_command(command, role)
    gui_update_command_list()

"""
Creates a phrase in graphical mode.
"""

def gui_create_phrase():
    language = phrases_language_entry.get()
    command = phrases_command_entry.get()
    response = phrases_response_entry.get()
    phrases = phrases_phrases_text.get("1.0", END)
    create_phrase(language, command, response, phrases)

"""
Removes phrase in graphical mode.
"""

def gui_remove_phrase():
    language = phrases_language_entry.get()
    command = phrases_command_entry.get()
    remove_phrase(language, command)

"""
Main.
"""

if __name__ == "__main__":
    if getuid() != 0:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Run it as root{DEFAULT}")
        exit()
    languages = get_installed_languages()
    if not languages:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}No languages found{DEFAULT}")
        exit()
    print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Starting settings...{DEFAULT}")
    try:
        root = Tk()
        root.attributes("-zoomed", True)
        root.title("Settings")
        canvas = Canvas(root)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar = Scrollbar(root, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        root_frame = Frame(canvas)
        canvas.create_window((0, 0), window=root_frame, anchor=N+W)

        rooms_devices_frame = LabelFrame(root_frame, text="Rooms & Devices", padx=5, pady=5)
        rooms_devices_frame.pack(side=TOP, padx=10, pady=10)

        rooms_frame = LabelFrame(rooms_devices_frame, padx=5, pady=5)
        rooms_frame.pack(side=TOP, pady=10)

        rooms_room_label = Label(rooms_frame, text="Room")
        rooms_room_label.pack(side=LEFT, padx=10)
        rooms_room_entry = Entry(rooms_frame)
        rooms_room_entry.pack(side=LEFT, padx=10)
        rooms_create_button = Button(rooms_frame, text="Create Room", command=gui_create_room)
        rooms_create_button.pack(side=LEFT, padx=10)
        rooms_remove_button = Button(rooms_frame, text="Remove Room", command=gui_remove_room)
        rooms_remove_button.pack(side=LEFT, padx=10)

        devices_frame = LabelFrame(rooms_devices_frame, padx=5, pady=5)
        devices_frame.pack(side=TOP, pady=10)

        devices_room_entry = StringVar(root_frame)
        devices_room_menu = OptionMenu(devices_frame, devices_room_entry, "")
        devices_room_menu.pack(side=LEFT, padx=10)
        gui_update_devices_room_menu()
        devices_position_entry = StringVar(root_frame)
        devices_position_entry.set(POSITIONS_IN_ROOM[0])
        devices_position_menu = OptionMenu(devices_frame, devices_position_entry, *POSITIONS_IN_ROOM)
        devices_position_menu.pack(side=LEFT, padx=10)
        devices_create_button = Button(devices_frame, text="Create Device", command=gui_create_device)
        devices_create_button.pack(side=LEFT, padx=10)
        devices_remove_button = Button(devices_frame, text="Remove Device", command=gui_remove_device)
        devices_remove_button.pack(side=LEFT, padx=10)
        devices_install_button = Button(devices_frame, text="Install Device", command=gui_install_device)
        devices_install_button.pack(side=LEFT, padx=10)
        rooms_devices_list = Listbox(devices_frame)
        rooms_devices_list.pack(side=LEFT, padx=10)
        gui_update_rooms_devices_list()

        users_roles_frame = LabelFrame(root_frame, text="Users & Roles", padx=5, pady=5)
        users_roles_frame.pack(side=TOP, padx=10, pady=10)

        users_frame = LabelFrame(users_roles_frame, padx=5, pady=5)
        users_frame.pack(side=TOP, pady=10)

        users_name_label = Label(users_frame, text="Name")
        users_name_label.pack(side=LEFT, padx=10)
        users_name_entry = Entry(users_frame)
        users_name_entry.pack(side=LEFT, padx=10)
        users_birth_date_label = Label(users_frame, text="Birth Date")
        users_birth_date_label.pack(side=LEFT, padx=10)
        users_birth_date_entry = Entry(users_frame)
        users_birth_date_entry.pack(side=LEFT, padx=10)
        users_language_entry = StringVar(root_frame)
        users_language_entry.set(languages[0])
        users_language_menu = OptionMenu(users_frame, users_language_entry, *languages)
        users_language_menu.pack(side=LEFT, padx=10)
        users_create_button = Button(users_frame, text="Create User", command=gui_create_user)
        users_create_button.pack(side=LEFT, padx=10)
        user_remove_button = Button(users_frame, text="Remove User", command=gui_remove_user)
        user_remove_button.pack(side=LEFT, padx=10)
        users_list = Listbox(users_frame)
        users_list.pack(side=LEFT, padx=10)
        gui_update_users_list()

        roles_frame = Frame(users_roles_frame)
        roles_frame.pack(side=TOP, pady=10)

        roles_1_frame = LabelFrame(roles_frame, padx=5, pady=5)
        roles_1_frame.pack(side=TOP, pady=10)

        roles_role_label = Label(roles_1_frame, text="Role")
        roles_role_label.pack(side=LEFT, padx=10)
        roles_role_entry = Entry(roles_1_frame)
        roles_role_entry.pack(side=LEFT, padx=10)
        roles_age_restriction_entry = BooleanVar()
        roles_age_restriction_check = Checkbutton(roles_1_frame, text="Age Restriction", variable=roles_age_restriction_entry)
        roles_age_restriction_check.pack(side=LEFT, padx=10)
        roles_create_button = Button(roles_1_frame, text="Create Role", command=gui_create_role)
        roles_create_button.pack(side=LEFT, padx=10)
        role_remove_button = Button(roles_1_frame, text="Remove Role", command=gui_remove_role)
        role_remove_button.pack(side=LEFT, padx=10)

        roles_2_frame = LabelFrame(roles_frame, padx=5, pady=5)
        roles_2_frame.pack(side=TOP, pady=10)

        roles_users_role_entry = StringVar(root_frame)
        roles_users_role_menu = OptionMenu(roles_2_frame, roles_users_role_entry, "")
        roles_users_role_menu.pack(side=LEFT, padx=10)
        gui_update_roles_users_role_menu()
        roles_users_user_entry = StringVar(root_frame)
        roles_users_user_menu = OptionMenu(roles_2_frame, roles_users_user_entry, "")
        roles_users_user_menu.pack(side=LEFT, padx=10)
        gui_update_roles_users_user_menu()
        roles_assignment_button = Button(roles_2_frame, text="Assign role", command=gui_assign_role)
        roles_assignment_button.pack(side=LEFT, padx=10)
        roles_deassignment_button = Button(roles_2_frame, text="Deassign role", command=gui_deassign_role)
        roles_deassignment_button.pack(side=LEFT, padx=10)
        roles_list = Listbox(roles_2_frame)
        roles_list.pack(side=LEFT, padx=10)
        gui_update_roles_list()

        commands_phrases_frame = LabelFrame( root_frame, text="Commands & Phrases", padx=5, pady=5)
        commands_phrases_frame.pack(side=TOP, padx=10, pady=10)

        commands_frame = Frame(commands_phrases_frame)
        commands_frame.pack(side=TOP, pady=10)

        commands_1_frame = LabelFrame(commands_frame, padx=5, pady=5)
        commands_1_frame.pack(side=TOP, pady=10)

        commands_command_label = Label(commands_1_frame, text="Command")
        commands_command_label.pack(side=LEFT, padx=10)
        commands_command_entry = Entry(commands_1_frame)
        commands_command_entry.pack(side=LEFT, padx=10)
        commands_description_label = Label(commands_1_frame, text="Description")
        commands_description_label.pack(side=LEFT, padx=10)
        commands_description_entry = Entry(commands_1_frame)
        commands_description_entry.pack(side=LEFT, padx=10)
        commands_local_entry = BooleanVar()
        commands_local_check = Checkbutton(commands_1_frame, text="Local command", variable=commands_local_entry)
        commands_local_check.pack(side=LEFT, padx=10)
        commands_create_button = Button(commands_1_frame, text="Create Command", command=gui_create_command)
        commands_create_button.pack(side=LEFT, padx=10)
        commands_remove_button = Button(commands_1_frame, text="Remove Command", command=gui_remove_command)
        commands_remove_button.pack(side=LEFT, padx=10)

        commands_2_frame = LabelFrame(commands_frame, padx=5, pady=5)
        commands_2_frame.pack(side=TOP, pady=10)

        commands_roles_command_entry = StringVar(root_frame)
        commands_roles_command_menu = OptionMenu(commands_2_frame, commands_roles_command_entry, "")
        commands_roles_command_menu.pack(side=LEFT, padx=10)
        gui_update_commands_roles_command_menu()
        commands_roles_role_entry = StringVar(root_frame)
        commands_roles_role_menu = OptionMenu(commands_2_frame, commands_roles_role_entry, "")
        commands_roles_role_menu.pack(side=LEFT, padx=10)
        gui_update_commands_roles_role_menu()
        commands_assignment_button = Button(commands_2_frame, text="Assign command", command=gui_assign_command)
        commands_assignment_button.pack(side=LEFT, padx=10)
        commands_deassignment_button = Button(commands_2_frame, text="Deassign command", command=gui_deassign_command)
        commands_deassignment_button.pack(side=LEFT, padx=10)
        commands_list = Listbox(commands_2_frame)
        commands_list.pack(side=LEFT, padx=10)
        gui_update_command_list()

        phrases_frame = LabelFrame(commands_phrases_frame, padx=5, pady=5)
        phrases_frame.pack(side=TOP, pady=10)

        phrases_1_frame = Frame(phrases_frame)
        phrases_1_frame.pack(side=TOP, pady=10)

        phrases_command_entry = StringVar(root_frame)
        phrases_command_menu = OptionMenu(phrases_1_frame, phrases_command_entry, "")
        phrases_command_menu.pack(side=LEFT, padx=10)
        gui_update_phrases_command_menu()
        phrases_language_entry = StringVar(root_frame)
        phrases_language_entry.set(languages[0])
        phrases_language_menu = OptionMenu(phrases_1_frame, phrases_language_entry, *languages)
        phrases_language_menu.pack(side=LEFT, padx=10)
        phrases_response_label = Label(phrases_1_frame, text="Response")
        phrases_response_label.pack(side=LEFT, padx=10)
        phrases_response_entry = Entry(phrases_1_frame)
        phrases_response_entry.pack(side=LEFT, padx=10)

        phrases_2_frame = Frame(phrases_frame)
        phrases_2_frame.pack(side=TOP, pady=10)

        phrases_phrases_label = Label(phrases_2_frame, text="Phrases")
        phrases_phrases_label.pack(side=LEFT, padx=10)
        phrases_phrases_text = Text(phrases_2_frame, width=50, height=10)
        phrases_phrases_text.pack(side=LEFT, padx=10)
        phrases_create_button = Button(phrases_2_frame, text="Create Phrase", command=gui_create_phrase)
        phrases_create_button.pack(side=LEFT, padx=10)
        phrases_remove_button = Button(phrases_2_frame, text="Remove Phrase", command=gui_remove_phrase)
        phrases_remove_button.pack(side=LEFT, padx=10)

        root_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox(ALL))
        root.mainloop()
        print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Exiting settings...{DEFAULT}")
    except KeyboardInterrupt:
        print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Exiting settings...{DEFAULT}")
