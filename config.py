#!/usr/bin/env python3

from constants import BLUE, DEFAULT, POSITIONS_IN_ROOM, RED, YELLOW

from commands import create_command, get_commands, remove_command, assign_command, deassign_command
from devices import create_device, install_device, remove_device
from languages import get_installed_languages
from phrases import create_phrase, remove_phrase
from roles import create_role, get_roles, remove_role, assign_role, deassign_role
from rooms import create_room, get_rooms, remove_room
from users import create_user, get_users, remove_user

from tkinter import BooleanVar, BOTH, Button, Checkbutton, END, Entry, Frame, Label, LEFT, Listbox, OptionMenu, StringVar, Text, Tk, ttk, TOP

"""
Settings GUI
"""

class Config(Tk):

    """
    Creates a room in graphical mode.
    """

    def gui_create_room(self):
        create_room(self.rooms_room_entry.get())
        Config.gui_update_rooms_list(self)
        Config.gui_update_devices_room_menu(self)

    """
    Removes a room in graphical mode.
    """

    def gui_remove_room(self):
        remove_room(self.rooms_room_entry.get())
        Config.gui_update_rooms_list(self)
        Config.gui_update_devices_list(self)
        Config.gui_update_devices_room_menu(self)

    """
    Creates a device in graphical mode.
    """

    def gui_create_device(self):
        create_device(self.devices_room_entry.get(), self.devices_position_entry.get())
        Config.gui_update_devices_list(self)

    """
    Removes a device in graphical mode.
    """

    def gui_remove_device(self):
        remove_device(self.devices_room_entry.get(), self.devices_position_entry.get())
        Config.gui_update_devices_list(self)

    """
    Installs a device in graphical mode.
    """

    def gui_install_device(self):
        install_device(self.devices_room_entry.get(), self.devices_position_entry.get())
        Config.gui_update_devices_list(self)

    """
    Creates a user in graphical mode.
    """

    def gui_create_user(self):
        create_user(self.users_name_entry.get(), self.users_birth_date_entry.get(), self.users_language_entry.get())
        Config.gui_update_users_list(self)
        Config.gui_update_roles_user_menu(self)

    """
    Removes a user in graphical mode.
    """

    def gui_remove_user(self):
        remove_user(self.users_name_entry.get())
        Config.gui_update_users_list(self)
        Config.gui_update_roles_list(self)
        Config.gui_update_roles_user_menu(self)

    """
    Creates a role in graphical mode.
    """

    def gui_create_role(self):
        create_role(self.roles_role_entry.get(), self.roles_age_restriction_entry.get())
        Config.gui_update_roles_list(self)
        Config.gui_update_roles_role_menu(self)
        Config.gui_update_commands_role_menu(self)

    """
    Removes a role in graphical mode.
    """

    def gui_remove_role(self):
        remove_role(self.roles_role_entry.get())
        Config.gui_update_roles_list(self)
        Config.gui_update_commands_list(self)
        Config.gui_update_roles_role_menu(self)
        Config.gui_update_commands_role_menu(self)

    """
    Assign a role to a user in graphical mode.
    """

    def gui_assign_role(self):
        assign_role(self.roles_assignment_role_entry.get(), self.roles_assignment_user_entry.get())
        Config.gui_update_roles_list(self)

    """
    Deassign a role from a user in graphical mode.
    """

    def gui_deassign_role(self):
        deassign_role(self.roles_assignment_role_entry.get(), self.roles_assignment_user_entry.get())
        Config.gui_update_roles_list(self)

    """
    Creates a command in graphical mode.
    """

    def gui_create_command(self):
        create_command(self.commands_command_entry.get(), self.commands_description_entry.get(), self.commands_local_entry.get())
        Config.gui_update_commands_list(self)
        Config.gui_update_commands_command_menu(self)
        Config.gui_update_phrases_command_menu(self)

    """
    Removes a command in graphical mode.
    """

    def gui_remove_command(self):
        remove_command(self.commands_command_entry.get())
        Config.gui_update_commands_list(self)
        Config.gui_update_commands_command_menu(self)
        Config.gui_update_phrases_command_menu(self)

    """
    Assign a command to a role in graphical mode.
    """

    def gui_assign_command(self):
        assign_command(self.commands_assignment_command_entry.get(), self.commands_assignment_role_entry.get())
        Config.gui_update_commands_list(self)

    """
    Deassign a command from a role in graphical mode.
    """

    def gui_deassign_command(self):
        deassign_command(self.commands_assignment_command_entry.get(), self.commands_assignment_role_entry.get())
        Config.gui_update_commands_list(self)

    """
    Creates a phrase in graphical mode.
    """

    def gui_create_phrase(self):
        create_phrase(self.phrases_language_entry.get(), self.phrases_command_entry.get(), self.phrases_response_entry.get(), self.phrases_phrases_text.get("1.0", END))

    """
    Removes phrase in graphical mode.
    """

    def gui_remove_phrase(self):
        remove_phrase(self.phrases_language_entry.get(), self.phrases_command_entry.get())

    """
    Update room's list in graphical mode.
    """

    def gui_update_rooms_list(self):
        self.rooms_list.delete(0, END)
        rooms = get_rooms()
        if rooms:
            for room in rooms:
                self.rooms_list.insert(END, room["room"])
        else:
            self.rooms_list.insert(END, "Non existing rooms...")
        self.rooms_list.config(width=max([len(room) for room in self.rooms_list.get(0, END)]))
        self.rooms_list.config(height=self.rooms_list.size())

    """
    Update device's list in graphical mode.
    """

    def gui_update_devices_list(self):
        self.devices_list.delete(0, END)
        rooms = get_rooms()
        if rooms:
            for room in rooms:
                if room["devices"]:
                    self.devices_list.insert(END, room["room"] + " [ " + ", ".join([device["position"] if device["installed"] else device["position"] + " (not installed)" for device in room["devices"]]) + " ]")
        else:
            self.devices_list.insert(END, "Non existing devices...")
        self.devices_list.config(width=max([len(room) for room in self.devices_list.get(0, END)]))
        self.devices_list.config(height=self.devices_list.size())

    """
    Update user's list in graphical mode.
    """

    def gui_update_users_list(self):
        self.users_list.delete(0, END)
        users = get_users()
        if users:
            for user in users:
                self.users_list.insert(END, user["name"] + " [ " + str(user["age"]) + " years ] [ " + user["language"] + " ]")
        else:
            self.users_list.insert(END, "Non existing users...")
        self.users_list.config(width=max([len(user) for user in self.users_list.get(0, END)]))
        self.users_list.config(height=self.users_list.size())

    """
    Update role's list in graphical mode.
    """

    def gui_update_roles_list(self):
        self.roles_list.delete(0, END)
        roles = get_roles()
        if roles:
            for role in roles:
                self.roles_list.insert(END, role["role"] + " [ age restriction: " + str(role["age_restriction"]) + " ] [ " + ", ".join(role["users"]) + " ]")
        else:
            self.roles_list.insert(END, "Non existing roles...")
        self.roles_list.config(width=max([len(role) for role in self.roles_list.get(0, END)]))
        self.roles_list.config(height=self.roles_list.size())

    """
    Update command's list in graphical mode.
    """

    def gui_update_commands_list(self):
        self.commands_list.delete(0, END)
        commands = get_commands()
        if commands:
            for command in commands:
                self.commands_list.insert(END, command["description"] + " [ local: " + str(command["local"]) + " ] [ " + ", ".join(command["roles"]) + " ]")
        else:
            self.commands_list.insert(END, "Non existing commands...")
        self.commands_list.config(width=max([len(command) for command in self.commands_list.get(0, END)]))
        self.commands_list.config(height=self.commands_list.size())

    """
    Update device's room menu in graphical mode.
    """

    def gui_update_devices_room_menu(self):
        self.devices_room_menu["menu"].delete(0, END)
        rooms = get_rooms()
        if rooms:
            for room in rooms:
                self.devices_room_menu["menu"].add_command(label=room["room"], command=lambda value=room["room"]: self.devices_room_entry.set(value))
            self.devices_room_entry.set(rooms[0]["room"])
        else:
            self.devices_room_menu["menu"].add_command(label="", command=lambda value="": self.devices_room_entry.set(value))
            self.devices_room_entry.set("")

    """
    Update role's user assignation menu in graphical mode.
    """

    def gui_update_roles_user_menu(self):
        self.roles_user_menu["menu"].delete(0, END)
        users = get_users()
        if users:
            for user in users:
                self.roles_user_menu["menu"].add_command(label=user["name"], command=lambda value=user["name"]: self.roles_assignment_user_entry.set(value))
            self.roles_assignment_user_entry.set(users[0]["name"])
        else:
            self.roles_user_menu["menu"].add_command(label="", command=lambda value="": self.roles_assignment_user_entry.set(value))
            self.roles_assignment_user_entry.set("")

    """
    Update roles's role assignation menu in graphical mode.
    """

    def gui_update_roles_role_menu(self):
        self.roles_role_menu["menu"].delete(0, END)
        roles = get_roles()
        if roles:
            for role in roles:
                self.roles_role_menu["menu"].add_command(label=role["role"], command=lambda value=role["role"]: self.roles_assignment_role_entry.set(value))
            self.roles_assignment_role_entry.set(roles[0]["role"])
        else:
            self.roles_role_menu["menu"].add_command(label="", command=lambda value="": self.roles_assignment_role_entry.set(value))
            self.roles_assignment_role_entry.set("")

    """
    Update commands's command assignation menu in graphical mode.
    """

    def gui_update_commands_command_menu(self):
        self.commands_command_menu["menu"].delete(0, END)
        commands = get_commands()
        if commands:
            for command in commands:
                self.commands_command_menu["menu"].add_command(label=command["description"], command=lambda value=command["command"]: self.commands_assignment_command_entry.set(value))
            self.commands_assignment_command_entry.set(commands[0]["command"])
        else:
            self.commands_command_menu["menu"].add_command(label="", command=lambda value="": self.commands_assignment_command_entry.set(value))
            self.commands_assignment_command_entry.set("")

    """
    Update commands's role assignation menu in graphical mode.
    """

    def gui_update_commands_role_menu(self):
        self.commands_role_menu["menu"].delete(0, END)
        roles = get_roles()
        if roles:
            for role in roles:
                self.commands_role_menu["menu"].add_command(label=role["role"], command=lambda value=role["role"]: self.commands_assignment_role_entry.set(value))
            self.commands_assignment_role_entry.set(roles[0]["role"])
        else:
            self.commands_role_menu["menu"].add_command(label="", command=lambda value="": self.commands_assignment_role_entry.set(value))
            self.commands_assignment_role_entry.set("")

    """
    Update phrases's command menu in graphical mode.
    """

    def gui_update_phrases_command_menu(self):
        self.phrases_command_menu["menu"].delete(0, END)
        commands = get_commands()
        if commands:
            for command in commands:
                self.phrases_command_menu["menu"].add_command(label=command["description"], command=lambda value=command["command"]: self.phrases_command_entry.set(value))
            self.phrases_command_entry.set(commands[0]["command"])
        else:
            self.phrases_command_menu["menu"].add_command(label="", command=lambda value="": self.phrases_command_entry.set(value))
            self.phrases_command_entry.set("")

    """
    Constructs settings.
    """
    def __init__(self):
        super().__init__()
        self.title("Settings")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True)

        # Rooms

        self.rooms_frame = Frame(self.notebook)
        self.notebook.add(self.rooms_frame, text="Rooms")

        self.rooms_1_frame = Frame(self.rooms_frame)
        self.rooms_1_frame.pack(side=TOP, pady=10)

        self.rooms_room_label = Label(self.rooms_1_frame, text="Room")
        self.rooms_room_label.pack(side=LEFT, padx=10)
        self.rooms_room_entry = Entry(self.rooms_1_frame)
        self.rooms_room_entry.pack(side=LEFT, padx=10)
        self.rooms_create_button = Button(self.rooms_1_frame, text="Create", command=lambda: Config.gui_create_room(self))
        self.rooms_create_button.pack(side=LEFT, padx=10)
        self.rooms_remove_button = Button(self.rooms_1_frame, text="Remove", command=lambda: Config.gui_remove_room(self))
        self.rooms_remove_button.pack(side=LEFT, padx=10)

        self.rooms_2_frame = Frame(self.rooms_frame)
        self.rooms_2_frame.pack(side=TOP, pady=10)

        self.rooms_list = Listbox(self.rooms_2_frame)        
        self.rooms_list.pack(side=LEFT, padx=10)
        Config.gui_update_rooms_list(self)

        # Devices

        self.devices_frame = Frame(self.notebook)
        self.notebook.add(self.devices_frame, text="Devices")

        self.devices_1_frame = Frame(self.devices_frame)
        self.devices_1_frame.pack(side=TOP, pady=10)

        self.devices_room_entry = StringVar(self)
        self.devices_room_menu = OptionMenu(self.devices_1_frame, self.devices_room_entry, "")
        self.devices_room_menu.pack(side=LEFT, padx=10)
        Config.gui_update_devices_room_menu(self)
        self.devices_position_entry = StringVar(self)
        self.devices_position_entry.set(POSITIONS_IN_ROOM[0])
        self.devices_position_menu = OptionMenu(self.devices_1_frame, self.devices_position_entry, *POSITIONS_IN_ROOM)
        self.devices_position_menu.pack(side=LEFT, padx=10)
        self.devices_create_button = Button(self.devices_1_frame, text="Create", command=lambda: Config.gui_create_device(self))
        self.devices_create_button.pack(side=LEFT, padx=10)
        self.devices_remove_button = Button(self.devices_1_frame, text="Remove", command=lambda: Config.gui_remove_device(self))
        self.devices_remove_button.pack(side=LEFT, padx=10)
        self.devices_install_button = Button(self.devices_1_frame, text="Install", command=lambda: Config.gui_install_device(self))
        self.devices_install_button.pack(side=LEFT, padx=10)

        self.devices_2_frame = Frame(self.devices_frame)
        self.devices_2_frame.pack(side=TOP, pady=10)

        self.devices_list = Listbox(self.devices_2_frame)
        self.devices_list.pack(side=LEFT, padx=10)
        Config.gui_update_devices_list(self)

        # Users
        
        self.users_frame = Frame(self.notebook)
        self.notebook.add(self.users_frame, text="Users")

        self.users_1_frame = Frame(self.users_frame)
        self.users_1_frame.pack(side=TOP, pady=10)

        self.users_name_label = Label(self.users_1_frame, text="Name")
        self.users_name_label.pack(side=LEFT, padx=10)
        self.users_name_entry = Entry(self.users_1_frame)
        self.users_name_entry.pack(side=LEFT, padx=10)
        self.users_birth_date_label = Label(self.users_1_frame, text="Birth Date")
        self.users_birth_date_label.pack(side=LEFT, padx=10)
        self.users_birth_date_entry = Entry(self.users_1_frame)
        self.users_birth_date_entry.pack(side=LEFT, padx=10)
        self.users_language_entry = StringVar(self)
        self.users_language_entry.set(languages[0])
        self.users_language_menu = OptionMenu(self.users_1_frame, self.users_language_entry, *languages)
        self.users_language_menu.pack(side=LEFT, padx=10)
        self.users_create_button = Button(self.users_1_frame, text="Create", command=lambda: Config.gui_create_user(self))
        self.users_create_button.pack(side=LEFT, padx=10)
        self.user_remove_button = Button(self.users_1_frame, text="Remove", command=lambda: Config.gui_remove_user(self))
        self.user_remove_button.pack(side=LEFT, padx=10)
        
        self.users_2_frame = Frame(self.users_frame)
        self.users_2_frame.pack(side=TOP, pady=10)
        
        self.users_list = Listbox(self.users_2_frame)
        self.users_list.pack(side=LEFT, padx=10)
        Config.gui_update_users_list(self)

        # Roles

        self.roles_frame = Frame(self.notebook)
        self.notebook.add(self.roles_frame, text="Roles")

        self.roles_1_frame = Frame(self.roles_frame)
        self.roles_1_frame.pack(side=TOP, pady=10)

        self.roles_role_label = Label(self.roles_1_frame, text="Role")
        self.roles_role_label.pack(side=LEFT, padx=10)
        self.roles_role_entry = Entry(self.roles_1_frame)
        self.roles_role_entry.pack(side=LEFT, padx=10)
        self.roles_age_restriction_entry = BooleanVar()
        self.roles_age_restriction_check = Checkbutton(self.roles_1_frame, text="Age Restriction", variable=self.roles_age_restriction_entry)
        self.roles_age_restriction_check.pack(side=LEFT, padx=10)
        self.roles_create_button = Button(self.roles_1_frame, text="Create", command=lambda: Config.gui_create_role(self))
        self.roles_create_button.pack(side=LEFT, padx=10)
        self.role_remove_button = Button(self.roles_1_frame, text="Remove", command=lambda: Config.gui_remove_role(self))
        self.role_remove_button.pack(side=LEFT, padx=10)

        self.roles_2_frame = Frame(self.roles_frame)
        self.roles_2_frame.pack(side=TOP, pady=10)

        self.roles_assignment_role_entry = StringVar(self)
        self.roles_role_menu = OptionMenu(self.roles_2_frame, self.roles_assignment_role_entry, "")
        self.roles_role_menu.pack(side=LEFT, padx=10)
        Config.gui_update_roles_role_menu(self)
        self.roles_assignment_user_entry = StringVar(self)
        self.roles_user_menu = OptionMenu(self.roles_2_frame, self.roles_assignment_user_entry, "")
        self.roles_user_menu.pack(side=LEFT, padx=10)
        Config.gui_update_roles_user_menu(self)
        self.roles_assignment_button = Button(self.roles_2_frame, text="Assign", command=lambda: Config.gui_assign_role(self))
        self.roles_assignment_button.pack(side=LEFT, padx=10)
        self.roles_deassignment_button = Button(self.roles_2_frame, text="Deassign", command=lambda: Config.gui_deassign_role(self))
        self.roles_deassignment_button.pack(side=LEFT, padx=10)

        self.roles_3_frame = Frame(self.roles_frame)
        self.roles_3_frame.pack(side=TOP, pady=10)

        self.roles_list = Listbox(self.roles_3_frame)
        self.roles_list.pack(side=LEFT, padx=10)
        Config.gui_update_roles_list(self)

        # Commands

        self.commands_frame = Frame(self.notebook)
        self.notebook.add(self.commands_frame, text="Commands")

        self.commands_1_frame = Frame(self.commands_frame)
        self.commands_1_frame.pack(side=TOP, pady=10)

        self.commands_command_label = Label(self.commands_1_frame, text="Command")
        self.commands_command_label.pack(side=LEFT, padx=10)
        self.commands_command_entry = Entry(self.commands_1_frame)
        self.commands_command_entry.pack(side=LEFT, padx=10)
        self.commands_description_label = Label(self.commands_1_frame, text="Description")
        self.commands_description_label.pack(side=LEFT, padx=10)
        self.commands_description_entry = Entry(self.commands_1_frame)
        self.commands_description_entry.pack(side=LEFT, padx=10)
        self.commands_local_entry = BooleanVar()
        self.commands_local_check = Checkbutton(self.commands_1_frame, text="Execute Locally", variable=self.commands_local_entry)
        self.commands_local_check.pack(side=LEFT, padx=10)
        self.commands_create_button = Button(self.commands_1_frame, text="Create", command=lambda: Config.gui_create_command(self))
        self.commands_create_button.pack(side=LEFT, padx=10)
        self.commands_remove_button = Button(self.commands_1_frame, text="Remove", command=lambda: Config.gui_remove_command(self))
        self.commands_remove_button.pack(side=LEFT, padx=10)

        self.commands_2_frame = Frame(self.commands_frame)
        self.commands_2_frame.pack(side=TOP, pady=10)

        self.commands_assignment_command_entry = StringVar(self)
        self.commands_command_menu = OptionMenu(self.commands_2_frame, self.commands_assignment_command_entry, "")
        self.commands_command_menu.pack(side=LEFT, padx=10)
        Config.gui_update_commands_command_menu(self)
        self.commands_assignment_role_entry = StringVar(self)
        self.commands_role_menu = OptionMenu(self.commands_2_frame, self.commands_assignment_role_entry, "")
        self.commands_role_menu.pack(side=LEFT, padx=10)
        Config.gui_update_commands_role_menu(self)
        self.commands_assignment_button = Button(self.commands_2_frame, text="Assign", command=lambda: Config.gui_assign_command(self))
        self.commands_assignment_button.pack(side=LEFT, padx=10)
        self.commands_deassignment_button = Button(self.commands_2_frame, text="Deassign", command=lambda: Config.gui_deassign_command(self))
        self.commands_deassignment_button.pack(side=LEFT, padx=10)

        self.commands_3_frame = Frame(self.commands_frame)
        self.commands_3_frame.pack(side=TOP, pady=10)

        self.commands_list = Listbox(self.commands_3_frame)
        self.commands_list.pack(side=LEFT, padx=10)
        Config.gui_update_commands_list(self)

        # Phrases

        self.phrases_frame = Frame(self.notebook)
        self.notebook.add(self.phrases_frame, text="Phrases")

        self.phrases_1_frame = Frame(self.phrases_frame)
        self.phrases_1_frame.pack(side=TOP, pady=10)

        self.phrases_command_entry = StringVar(self)
        self.phrases_command_menu = OptionMenu(self.phrases_1_frame, self.phrases_command_entry, "")
        self.phrases_command_menu.pack(side=LEFT, padx=10)
        Config.gui_update_phrases_command_menu(self)
        self.phrases_language_entry = StringVar(self)
        self.phrases_language_entry.set(languages[0])
        self.phrases_language_menu = OptionMenu(self.phrases_1_frame, self.phrases_language_entry, *languages)
        self.phrases_language_menu.pack(side=LEFT, padx=10)
        self.phrases_response_label = Label(self.phrases_1_frame, text="Response")
        self.phrases_response_label.pack(side=LEFT, padx=10)
        self.phrases_response_entry = Entry(self.phrases_1_frame)
        self.phrases_response_entry.pack(side=LEFT, padx=10)

        self.phrases_2_frame = Frame(self.phrases_frame)
        self.phrases_2_frame.pack(side=TOP, pady=10)

        self.phrases_phrases_label = Label(self.phrases_2_frame, text="Phrases")
        self.phrases_phrases_label.pack(side=LEFT, padx=10)
        self.phrases_phrases_text = Text(self.phrases_2_frame, width=50, height=10)
        self.phrases_phrases_text.pack(side=LEFT, padx=10)
        self.phrases_create_button = Button(self.phrases_2_frame, text="Create", command=lambda: Config.gui_create_phrase(self))
        self.phrases_create_button.pack(side=LEFT, padx=10)
        self.phrases_remove_button = Button(self.phrases_2_frame, text="Remove", command=lambda: Config.gui_remove_phrase(self))
        self.phrases_remove_button.pack(side=LEFT, padx=10)

        self.update_idletasks()
        self.geometry('{}x{}+{}+{}'.format(self.winfo_width(), self.winfo_height(), (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2), (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)))

"""
Main.
"""

if __name__ == "__main__":
    languages = get_installed_languages()
    if not languages:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}No languages found{DEFAULT}")
        exit()
    print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Starting settings...{DEFAULT}")
    try:
        Config().mainloop()
    except KeyboardInterrupt:
        pass
    print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Exiting settings...{DEFAULT}")
    exit()
