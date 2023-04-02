#!/usr/bin/env python3

from ast import literal_eval
from Common.commands import create_local_command, create_remote_command, get_local_commands, get_remote_commands, remove_local_command, remove_remote_command
from Common.constants import BLUE, DEFAULT, RED, YELLOW
from Common.devices import create_device, get_devices, install_device, remove_device
from Common.general import get_legal_age, get_wifi_password, get_wifi_ssid, set_legal_age, set_wifi_credentials
from Common.languages import get_default_language, get_installed_languages, set_default_language
from Common.peripherals import assign_external_peripheral, deassign_external_peripheral, get_device_peripherals, get_external_peripherals, get_internal_peripherals, get_peripheral_actions, get_peripheral_subtypes
from Common.positions import create_position, get_positions, remove_position
from Common.roles import assign_role, create_role, deassign_role, get_roles, remove_role
from Common.rooms import create_room, get_rooms, remove_room
from Common.users import create_user, get_users, remove_user
from tkinter import BooleanVar, BOTH, Button, Checkbutton, END, Entry, Frame, Label, LEFT, Listbox, OptionMenu, StringVar, Text, Tk, ttk, TOP

"""
Settings GUI
"""

class Config(Tk):

    """
    Constructs GUI.
    """

    def __init__(self):
        super().__init__()
        self.title("Settings")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True)

        # General

        self.general_frame = Frame(self.notebook)
        self.notebook.add(self.general_frame, text="General")

        self.general_1_frame = Frame(self.general_frame)
        self.general_1_frame.pack(side=TOP, pady=10)

        self.general_language_label = Label(self.general_1_frame, text="Default Language")
        self.general_language_label.pack(side=LEFT, padx=10)
        self.general_language_entry = StringVar(self)
        self.general_language_entry.set(default_language)
        self.general_language_menu = OptionMenu(self.general_1_frame, self.general_language_entry, *languages, command=lambda selection: set_default_language(selection))
        self.general_language_menu.pack(side=LEFT, padx=10)

        self.general_2_frame = Frame(self.general_frame)
        self.general_2_frame.pack(side=TOP, pady=10)

        self.general_legal_age_label = Label(self.general_2_frame, text="Legal Age")
        self.general_legal_age_label.pack(side=LEFT, padx=10)
        self.general_legal_age_entry = Entry(self.general_2_frame)
        self.general_legal_age_entry.insert(0, get_legal_age())
        self.general_legal_age_entry.pack(side=LEFT, padx=10)
        self.general_legal_age_set_button = Button(self.general_2_frame, text="Set", command=lambda: set_legal_age(self.general_legal_age_entry.get()))
        self.general_legal_age_set_button.pack(side=LEFT, padx=10)

        self.general_3_frame = Frame(self.general_frame)
        self.general_3_frame.pack(side=TOP, pady=10)

        self.general_wifi_ssid_label = Label(self.general_3_frame, text="Wifi SSID")
        self.general_wifi_ssid_label.pack(side=LEFT, padx=10)
        self.general_wifi_ssid_entry = Entry(self.general_3_frame)
        self.general_wifi_ssid_entry.insert(0, get_wifi_ssid())
        self.general_wifi_ssid_entry.pack(side=LEFT, padx=10)
        self.general_wifi_password_label = Label(self.general_3_frame, text="Wifi Password")
        self.general_wifi_password_label.pack(side=LEFT, padx=10)
        self.general_wifi_password_entry = Entry(self.general_3_frame, show="*")
        self.general_wifi_password_entry.insert(0, get_wifi_password())
        self.general_wifi_password_entry.pack(side=LEFT, padx=10)
        self.general_wifi_credentials_set_button = Button(self.general_3_frame, text="Set", command=lambda: set_wifi_credentials(self.general_wifi_ssid_entry.get(), self.general_wifi_password_entry.get()))
        self.general_wifi_credentials_set_button.pack(side=LEFT, padx=10)

        # TODO: Add automatic start on boot option

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
        self.users_create_button = Button(self.users_1_frame, text="Create", command=lambda: Config.gui_create_user(self))
        self.users_create_button.pack(side=LEFT, padx=10)
        self.user_remove_button = Button(self.users_1_frame, text="Remove", command=lambda: Config.gui_remove_user(self))
        self.user_remove_button.pack(side=LEFT, padx=10)
        
        self.users_2_frame = Frame(self.users_frame)
        self.users_2_frame.pack(side=TOP, pady=10)
        
        self.users_users_label = Label(self.users_2_frame, text="Users")
        self.users_users_label.pack(side=LEFT, padx=10)
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
        self.roles_privileged_entry = BooleanVar()
        self.roles_privileged_check = Checkbutton(self.roles_1_frame, text="Privileged", variable=self.roles_privileged_entry)
        self.roles_privileged_check.pack(side=LEFT, padx=10)
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

        self.roles_roles_label = Label(self.roles_3_frame, text="Roles")
        self.roles_roles_label.pack(side=LEFT, padx=10)
        self.roles_list = Listbox(self.roles_3_frame)
        self.roles_list.pack(side=LEFT, padx=10)
        Config.gui_update_roles_list(self)

        # Peripherals

        self.peripherals_frame = Frame(self.notebook)
        self.notebook.add(self.peripherals_frame, text="Peripherals")

        self.peripherals_1_frame = Frame(self.peripherals_frame)
        self.peripherals_1_frame.pack(side=TOP, pady=10)

        self.internal_peripherals_label = Label(self.peripherals_1_frame, text="Internal Peripherals")
        self.internal_peripherals_label.pack(side=LEFT, padx=10)
        self.internal_peripherals_list = Listbox(self.peripherals_1_frame)
        self.internal_peripherals_list.pack(side=LEFT, padx=10)
        Config.gui_update_internal_peripherals_list(self)

        self.peripherals_2_frame = Frame(self.peripherals_frame)
        self.peripherals_2_frame.pack(side=TOP, pady=10)
        
        self.external_peripherals_label = Label(self.peripherals_2_frame, text="External Peripherals")
        self.external_peripherals_label.pack(side=LEFT, padx=10)
        self.external_peripherals_list = Listbox(self.peripherals_2_frame)
        self.external_peripherals_list.pack(side=LEFT, padx=10)
        Config.gui_update_external_peripherals_list(self)

        # Positions & Rooms

        self.positions_rooms_frame = Frame(self.notebook)
        self.notebook.add(self.positions_rooms_frame, text="Positions & Rooms")

        self.positions_1_frame = Frame(self.positions_rooms_frame)
        self.positions_1_frame.pack(side=TOP, pady=10)

        self.positions_position_label = Label(self.positions_1_frame, text="Position")
        self.positions_position_label.pack(side=LEFT, padx=10)
        self.positions_position_entry = Entry(self.positions_1_frame)
        self.positions_position_entry.pack(side=LEFT, padx=10)
        self.positions_create_button = Button(self.positions_1_frame, text="Create", command=lambda: Config.gui_create_position(self))
        self.positions_create_button.pack(side=LEFT, padx=10)
        self.positions_remove_button = Button(self.positions_1_frame, text="Remove", command=lambda: Config.gui_remove_position(self))
        self.positions_remove_button.pack(side=LEFT, padx=10)

        self.positions_2_frame = Frame(self.positions_rooms_frame)
        self.positions_2_frame.pack(side=TOP, pady=10)

        self.positions_positions_label = Label(self.positions_2_frame, text="Positions")
        self.positions_positions_label.pack(side=LEFT, padx=10)
        self.positions_list = Listbox(self.positions_2_frame)
        self.positions_list.pack(side=LEFT, padx=10)
        Config.gui_update_positions_list(self)

        self.rooms_1_frame = Frame(self.positions_rooms_frame)
        self.rooms_1_frame.pack(side=TOP, pady=10)

        self.rooms_room_label = Label(self.rooms_1_frame, text="Room")
        self.rooms_room_label.pack(side=LEFT, padx=10)
        self.rooms_room_entry = Entry(self.rooms_1_frame)
        self.rooms_room_entry.pack(side=LEFT, padx=10)
        self.rooms_create_button = Button(self.rooms_1_frame, text="Create", command=lambda: Config.gui_create_room(self))
        self.rooms_create_button.pack(side=LEFT, padx=10)
        self.rooms_remove_button = Button(self.rooms_1_frame, text="Remove", command=lambda: Config.gui_remove_room(self))
        self.rooms_remove_button.pack(side=LEFT, padx=10)

        self.rooms_2_frame = Frame(self.positions_rooms_frame)
        self.rooms_2_frame.pack(side=TOP, pady=10)

        self.rooms_rooms_label = Label(self.rooms_2_frame, text="Rooms")
        self.rooms_rooms_label.pack(side=LEFT, padx=10)
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
        self.devices_position_menu = OptionMenu(self.devices_1_frame, self.devices_position_entry, "")
        self.devices_position_menu.pack(side=LEFT, padx=10)
        Config.gui_update_devices_position_menu(self)
        self.devices_create_button = Button(self.devices_1_frame, text="Create", command=lambda: Config.gui_create_device(self))
        self.devices_create_button.pack(side=LEFT, padx=10)
        self.devices_remove_button = Button(self.devices_1_frame, text="Remove", command=lambda: Config.gui_remove_device(self))
        self.devices_remove_button.pack(side=LEFT, padx=10)
        self.devices_install_button = Button(self.devices_1_frame, text="Install", command=lambda: Config.gui_install_device(self))
        self.devices_install_button.pack(side=LEFT, padx=10)

        self.devices_2_frame = Frame(self.devices_frame)
        self.devices_2_frame.pack(side=TOP, pady=10)

        self.devices_peripheral_entry = StringVar(self)
        self.devices_peripheral_menu = OptionMenu(self.devices_2_frame, self.devices_peripheral_entry, "")
        self.devices_peripheral_menu.pack(side=LEFT, padx=10)
        Config.gui_update_devices_peripheral_menu(self)
        self.devices_device_entry = StringVar(self)
        self.devices_device_menu = OptionMenu(self.devices_2_frame, self.devices_device_entry, "")
        self.devices_device_menu.pack(side=LEFT, padx=10)
        Config.gui_update_devices_device_menu(self)
        self.devices_assignment_button = Button(self.devices_2_frame, text="Assign", command=lambda: Config.gui_assign_peripheral(self))
        self.devices_assignment_button.pack(side=LEFT, padx=10)
        self.devices_deassignment_button = Button(self.devices_2_frame, text="Deassign", command=lambda: Config.gui_deassign_peripheral(self))
        self.devices_deassignment_button.pack(side=LEFT, padx=10)

        self.devices_3_frame = Frame(self.devices_frame)
        self.devices_3_frame.pack(side=TOP, pady=10)

        self.devices_devices_label = Label(self.devices_3_frame, text="Devices")
        self.devices_devices_label.pack(side=LEFT, padx=10)
        self.devices_list = Listbox(self.devices_3_frame)
        self.devices_list.pack(side=LEFT, padx=10)
        Config.gui_update_devices_list(self)

        # Local Commands

        self.local_commands_frame = Frame(self.notebook)
        self.notebook.add(self.local_commands_frame, text="Local Commands")

        self.local_commands_1_frame = Frame(self.local_commands_frame)
        self.local_commands_1_frame.pack(side=TOP, pady=10)

        self.commands_command_label = Label(self.local_commands_1_frame, text="Command")
        self.commands_command_label.pack(side=LEFT, padx=10)
        self.commands_command_entry = Entry(self.local_commands_1_frame)
        self.commands_command_entry.pack(side=LEFT, padx=10)
        self.local_commands_description_label = Label(self.local_commands_1_frame, text="Description")
        self.local_commands_description_label.pack(side=LEFT, padx=10)
        self.local_commands_description_entry = Entry(self.local_commands_1_frame)
        self.local_commands_description_entry.pack(side=LEFT, padx=10)

        self.local_commands_2_frame = Frame(self.local_commands_frame)
        self.local_commands_2_frame.pack(side=TOP, pady=10)

        self.local_commands_response_label = Label(self.local_commands_2_frame, text="Response")
        self.local_commands_response_label.pack(side=LEFT, padx=10)
        self.local_commands_response_entry = Entry(self.local_commands_2_frame)
        self.local_commands_response_entry.pack(side=LEFT, padx=10)
        self.local_commands_phrases_label = Label(self.local_commands_2_frame, text="Phrases")
        self.local_commands_phrases_label.pack(side=LEFT, padx=10)
        self.local_commands_phrases_text = Text(self.local_commands_2_frame, width=50, height=10)
        self.local_commands_phrases_text.pack(side=LEFT, padx=10)

        self.local_commands_3_frame = Frame(self.local_commands_frame)
        self.local_commands_3_frame.pack(side=TOP, pady=10)

        self.local_commands_age_restriction_entry = BooleanVar()
        self.local_commands_age_restriction_check = Checkbutton(self.local_commands_3_frame, text="Age Restriction", variable=self.local_commands_age_restriction_entry)
        self.local_commands_age_restriction_check.pack(side=LEFT, padx=10)
        self.local_commands_privileged_entry = BooleanVar()
        self.local_commands_privileged_check = Checkbutton(self.local_commands_3_frame, text="Privileged", variable=self.local_commands_privileged_entry)
        self.local_commands_privileged_check.pack(side=LEFT, padx=10)
        self.local_commands_create_button = Button(self.local_commands_3_frame, text="Create", command=lambda: Config.gui_create_local_command(self))
        self.local_commands_create_button.pack(side=LEFT, padx=10)
        self.local_commands_remove_button = Button(self.local_commands_3_frame, text="Remove", command=lambda: Config.gui_remove_local_command(self))
        self.local_commands_remove_button.pack(side=LEFT, padx=10)

        self.local_commands_4_frame = Frame(self.local_commands_frame)
        self.local_commands_4_frame.pack(side=TOP, pady=10)

        self.local_commands_label = Label(self.local_commands_4_frame, text="Local Commands")
        self.local_commands_label.pack(side=LEFT, padx=10)
        self.local_commands_list = Listbox(self.local_commands_4_frame)
        self.local_commands_list.pack(side=LEFT, padx=10)
        Config.gui_update_local_commands_list(self)

        # Remote Commands

        self.remote_commands_frame = Frame(self.notebook)
        self.notebook.add(self.remote_commands_frame, text="Remote Commands")

        self.remote_commands_1_frame = Frame(self.remote_commands_frame)
        self.remote_commands_1_frame.pack(side=TOP, pady=10)

        self.commands_device_entry = StringVar(self)
        self.commands_device_menu = OptionMenu(self.remote_commands_1_frame, self.commands_device_entry, "")
        self.commands_device_menu.pack(side=LEFT, padx=10)
        Config.gui_update_commands_device_menu(self)
        self.commands_peripheral_entry = StringVar(self)
        self.commands_peripheral_menu = OptionMenu(self.remote_commands_1_frame, self.commands_peripheral_entry, "")
        self.commands_peripheral_menu.pack(side=LEFT, padx=10)
        Config.gui_update_commands_peripheral_menu(self)
        self.commands_subtype_entry = StringVar(self)
        self.commands_subtype_menu = OptionMenu(self.remote_commands_1_frame, self.commands_subtype_entry, "")
        self.commands_subtype_menu.pack(side=LEFT, padx=10)
        Config.gui_update_commands_subtype_menu(self)
        self.commands_action_entry = StringVar(self)
        self.commands_action_menu = OptionMenu(self.remote_commands_1_frame, self.commands_action_entry, "")
        self.commands_action_menu.pack(side=LEFT, padx=10)
        Config.gui_update_commands_action_menu(self)
        self.remote_commands_description_label = Label(self.remote_commands_1_frame, text="Description")
        self.remote_commands_description_label.pack(side=LEFT, padx=10)
        self.remote_commands_description_entry = Entry(self.remote_commands_1_frame)
        self.remote_commands_description_entry.pack(side=LEFT, padx=10)

        self.remote_commands_2_frame = Frame(self.remote_commands_frame)
        self.remote_commands_2_frame.pack(side=TOP, pady=10)

        self.remote_commands_response_label = Label(self.remote_commands_2_frame, text="Response")
        self.remote_commands_response_label.pack(side=LEFT, padx=10)
        self.remote_commands_response_entry = Entry(self.remote_commands_2_frame)
        self.remote_commands_response_entry.pack(side=LEFT, padx=10)
        self.remote_commands_phrases_label = Label(self.remote_commands_2_frame, text="Phrases")
        self.remote_commands_phrases_label.pack(side=LEFT, padx=10)
        self.remote_commands_phrases_text = Text(self.remote_commands_2_frame, width=50, height=10)
        self.remote_commands_phrases_text.pack(side=LEFT, padx=10)

        self.remote_commands_3_frame = Frame(self.remote_commands_frame)
        self.remote_commands_3_frame.pack(side=TOP, pady=10)

        self.remote_commands_age_restriction_entry = BooleanVar()
        self.remote_commands_age_restriction_check = Checkbutton(self.remote_commands_3_frame, text="Age Restriction", variable=self.remote_commands_age_restriction_entry)
        self.remote_commands_age_restriction_check.pack(side=LEFT, padx=10)
        self.remote_commands_privileged_entry = BooleanVar()
        self.remote_commands_privileged_check = Checkbutton(self.remote_commands_3_frame, text="Privileged", variable=self.remote_commands_privileged_entry)
        self.remote_commands_privileged_check.pack(side=LEFT, padx=10)
        self.remote_commands_create_button = Button(self.remote_commands_3_frame, text="Create", command=lambda: Config.gui_create_remote_command(self))
        self.remote_commands_create_button.pack(side=LEFT, padx=10)
        self.remote_commands_remove_button = Button(self.remote_commands_3_frame, text="Remove", command=lambda: Config.gui_remove_remote_command(self))
        self.remote_commands_remove_button.pack(side=LEFT, padx=10)

        self.remote_commands_4_frame = Frame(self.remote_commands_frame)
        self.remote_commands_4_frame.pack(side=TOP, pady=10)

        self.remote_commands_label = Label(self.remote_commands_4_frame, text="Remote Commands")
        self.remote_commands_label.pack(side=LEFT, padx=10)
        self.remote_commands_list = Listbox(self.remote_commands_4_frame)
        self.remote_commands_list.pack(side=LEFT, padx=10)
        Config.gui_update_remote_commands_list(self)

        self.update_idletasks()
        self.geometry('{}x{}+{}+{}'.format(self.winfo_width(), self.winfo_height(), (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2), (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)))

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
        Config.gui_update_devices_device_menu(self)
        Config.gui_update_commands_device_menu(self)
        Config.gui_update_commands_peripheral_menu(self)
        Config.gui_update_commands_subtype_menu(self)
        Config.gui_update_commands_action_menu(self)

    """
    Creates a position in graphical mode.
    """

    def gui_create_position(self):
        create_position(self.positions_position_entry.get())
        Config.gui_update_positions_list(self)
        Config.gui_update_devices_position_menu(self)

    """
    Removes a position in graphical mode.
    """

    def gui_remove_position(self):
        remove_position(self.positions_position_entry.get())
        Config.gui_update_positions_list(self)
        Config.gui_update_devices_list(self)
        Config.gui_update_devices_position_menu(self)
        Config.gui_update_devices_device_menu(self)
        Config.gui_update_commands_device_menu(self)
        Config.gui_update_commands_peripheral_menu(self)
        Config.gui_update_commands_subtype_menu(self)
        Config.gui_update_commands_action_menu(self)

    """
    Creates a device in graphical mode.
    """

    def gui_create_device(self):
        create_device(self.devices_room_entry.get(), self.devices_position_entry.get())
        Config.gui_update_devices_list(self)
        Config.gui_update_devices_device_menu(self)
        Config.gui_update_commands_device_menu(self)
        Config.gui_update_commands_peripheral_menu(self)
        Config.gui_update_commands_subtype_menu(self)
        Config.gui_update_commands_action_menu(self)

    """
    Removes a device in graphical mode.
    """

    def gui_remove_device(self):
        remove_device(self.devices_room_entry.get(), self.devices_position_entry.get())
        Config.gui_update_devices_list(self)
        Config.gui_update_devices_device_menu(self)
        Config.gui_update_commands_device_menu(self)
        Config.gui_update_commands_peripheral_menu(self)
        Config.gui_update_commands_subtype_menu(self)
        Config.gui_update_commands_action_menu(self)

    """
    Assigns a peripheral to a device in graphical mode.
    """

    def gui_assign_peripheral(self):
        assign_external_peripheral(self.devices_peripheral_entry.get(), literal_eval(self.devices_device_entry.get())[0] if self.devices_device_entry.get() else self.devices_device_entry.get(), literal_eval(self.devices_device_entry.get())[1] if self.devices_device_entry.get() else self.devices_device_entry.get())
        Config.gui_update_devices_list(self)
        Config.gui_update_commands_peripheral_menu(self)
        Config.gui_update_commands_subtype_menu(self)
        Config.gui_update_commands_action_menu(self)

    """
    Deassigns a peripheral from a device in graphical mode.
    """

    def gui_deassign_peripheral(self):
        deassign_external_peripheral(self.devices_peripheral_entry.get(), literal_eval(self.devices_device_entry.get())[0] if self.devices_device_entry.get() else self.devices_device_entry.get(), literal_eval(self.devices_device_entry.get())[1] if self.devices_device_entry.get() else self.devices_device_entry.get())
        Config.gui_update_devices_list(self)
        Config.gui_update_commands_peripheral_menu(self)
        Config.gui_update_commands_subtype_menu(self)
        Config.gui_update_commands_action_menu(self)

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
        create_user(self.users_name_entry.get(), self.users_birth_date_entry.get())
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
        create_role(self.roles_role_entry.get(), self.roles_age_restriction_entry.get(), self.roles_privileged_entry.get())
        Config.gui_update_roles_list(self)
        Config.gui_update_roles_role_menu(self)

    """
    Removes a role in graphical mode.
    """

    def gui_remove_role(self):
        remove_role(self.roles_role_entry.get())
        Config.gui_update_roles_list(self)
        Config.gui_update_roles_role_menu(self)

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
    Creates a local command in graphical mode.
    """

    def gui_create_local_command(self):
        create_local_command(self.commands_command_entry.get(), self.local_commands_description_entry.get(), self.local_commands_age_restriction_entry.get(), self.local_commands_privileged_entry.get(), self.local_commands_response_entry.get(), self.local_commands_phrases_text.get(1.0, END), self.general_language_entry.get())
        Config.gui_update_local_commands_list(self)

    """
    Removes a local command in graphical mode.
    """

    def gui_remove_local_command(self):
        remove_local_command(self.commands_command_entry.get())
        Config.gui_update_local_commands_list(self)

    """
    Creates a remote command in graphical mode.
    """

    def gui_create_remote_command(self):
        create_remote_command(self.commands_peripheral_entry.get(), self.commands_subtype_entry.get(), self.commands_action_entry.get(), literal_eval(self.devices_device_entry.get())[0] if self.devices_device_entry.get() else self.devices_device_entry.get(), literal_eval(self.devices_device_entry.get())[1] if self.devices_device_entry.get() else self.devices_device_entry.get(), self.remote_commands_description_entry.get(), self.remote_commands_age_restriction_entry.get(), self.remote_commands_privileged_entry.get(), self.remote_commands_response_entry.get(), self.remote_commands_phrases_text.get(1.0, END), self.general_language_entry.get())
        Config.gui_update_remote_commands_list(self)

    """
    Removes a remote command in graphical mode.
    """

    def gui_remove_remote_command(self):
        remove_remote_command(self.commands_peripheral_entry.get(), self.commands_subtype_entry.get(), self.commands_action_entry.get(), literal_eval(self.devices_device_entry.get())[0] if self.devices_device_entry.get() else self.devices_device_entry.get(), literal_eval(self.devices_device_entry.get())[1] if self.devices_device_entry.get() else self.devices_device_entry.get())
        Config.gui_update_remote_commands_list(self)

    """
    Update room's list in graphical mode.
    """

    def gui_update_rooms_list(self):
        self.rooms_list.delete(0, END)
        rooms = get_rooms()
        if rooms:
            for room in rooms:
                self.rooms_list.insert(END, room)
        else:
            self.rooms_list.insert(END, "Non existing rooms...")
        self.rooms_list.config(width=max([len(room) for room in self.rooms_list.get(0, END)]))
        self.rooms_list.config(height=self.rooms_list.size())

    """
    Update position's list in graphical mode.
    """

    def gui_update_positions_list(self):
        self.positions_list.delete(0, END)
        positions = get_positions()
        if positions:
            for position in positions:
                self.positions_list.insert(END, position)
        else:
            self.positions_list.insert(END, "Non existing positions...")
        self.positions_list.config(width=max([len(position) for position in self.positions_list.get(0, END)]))
        self.positions_list.config(height=self.positions_list.size())

    """
    Update internal peripheral's list in graphical mode.
    """

    def gui_update_internal_peripherals_list(self):
        self.internal_peripherals_list.delete(0, END)
        peripherals = get_internal_peripherals()
        if peripherals:
            for peripheral in peripherals:
                self.internal_peripherals_list.insert(END, peripheral["type"] + (" (sensor)" if peripheral["sensor"] else "") + (" (actuator)" if peripheral["actuator"] else ""))
        else:
            self.internal_peripherals_list.insert(END, "Non existing internal peripherals...")
        self.internal_peripherals_list.config(width=max([len(peripheral) for peripheral in self.internal_peripherals_list.get(0, END)]))
        self.internal_peripherals_list.config(height=self.internal_peripherals_list.size())
        
    """
    Update external peripheral's list in graphical mode.
    """

    def gui_update_external_peripherals_list(self):
        self.external_peripherals_list.delete(0, END)
        peripherals = get_external_peripherals()
        if peripherals:
            for peripheral in peripherals:
                self.external_peripherals_list.insert(END, peripheral["type"] + (" (sensor)" if peripheral["sensor"] else "") + (" (actuator)" if peripheral["actuator"] else ""))
        else:
            self.external_peripherals_list.insert(END, "Non existing internal peripherals...")
        self.external_peripherals_list.config(width=max([len(peripheral) for peripheral in self.external_peripherals_list.get(0, END)]))
        self.external_peripherals_list.config(height=self.external_peripherals_list.size())

    """
    Update device's list in graphical mode.
    """

    def gui_update_devices_list(self):
        self.devices_list.delete(0, END)
        devices = get_devices()
        if devices:
            for device in devices:
                self.devices_list.insert(END, device["room"] + " (" + device["position"] + ")" + (" (not installed)" if not device["installed"] else "") + " [ " + ", ".join(peripheral for peripheral in device["external_peripherals"]) + " ]")
        else:
            self.devices_list.insert(END, "Non existing devices...")
        self.devices_list.config(width=max([len(device) for device in self.devices_list.get(0, END)]))
        self.devices_list.config(height=self.devices_list.size())

    """
    Update user's list in graphical mode.
    """

    def gui_update_users_list(self):
        self.users_list.delete(0, END)
        users = get_users()
        if users:
            for user in users:
                self.users_list.insert(END, user["name"] + " [ " + str(user["age"]) + " years ]")
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
                self.roles_list.insert(END, role["role"] + (" (Age Restriction)" if role["age_restriction"] else "") + (" (Privileged)" if role["privileged"] else "") + " [ " + ", ".join(role["users"]) + " ]")
        else:
            self.roles_list.insert(END, "Non existing roles...")
        self.roles_list.config(width=max([len(role) for role in self.roles_list.get(0, END)]))
        self.roles_list.config(height=self.roles_list.size())

    """
    Update local command's list in graphical mode.
    """

    def gui_update_local_commands_list(self):
        self.local_commands_list.delete(0, END)
        commands = get_local_commands()
        if commands:
            for command in commands:
                self.local_commands_list.insert(END, command["description"] + (" (Age Restriction)" if command["age_restriction"] else "") + (" (Privileged)" if command["privileged"] else ""))
        else:
            self.local_commands_list.insert(END, "Non existing local commands...")
        self.local_commands_list.config(width=max([len(command) for command in self.local_commands_list.get(0, END)]))
        self.local_commands_list.config(height=self.local_commands_list.size())

    """
    Update remote command's list in graphical mode.
    """

    def gui_update_remote_commands_list(self):
        self.remote_commands_list.delete(0, END)
        commands = get_remote_commands()
        if commands:
            for command in commands:
                self.remote_commands_list.insert(END, command["description"] + (" (Age Restriction)" if command["age_restriction"] else "") + (" (Privileged)" if command["privileged"] else ""))
        else:
            self.remote_commands_list.insert(END, "Non existing remote commands...")
        self.remote_commands_list.config(width=max([len(command) for command in self.remote_commands_list.get(0, END)]))
        self.remote_commands_list.config(height=self.remote_commands_list.size())

    """
    Update device's room menu in graphical mode.
    """

    def gui_update_devices_room_menu(self):
        self.devices_room_menu["menu"].delete(0, END)
        rooms = get_rooms()
        if rooms:
            for room in rooms:
                self.devices_room_menu["menu"].add_command(label=room, command=lambda value=room: self.devices_room_entry.set(value))
            self.devices_room_entry.set(rooms[0])
        else:
            self.devices_room_entry.set("")

    """
    Update device's position menu in graphical mode.
    """

    def gui_update_devices_position_menu(self):
        self.devices_position_menu["menu"].delete(0, END)
        positions = get_positions()
        if positions:
            for position in positions:
                self.devices_position_menu["menu"].add_command(label=position, command=lambda value=position: self.devices_position_entry.set(value))
            self.devices_position_entry.set(positions[0])
        else:
            self.devices_position_entry.set("")

    """
    Update device's peripheral assignation menu in graphical mode.
    """

    def gui_update_devices_peripheral_menu(self):
        self.devices_peripheral_menu["menu"].delete(0, END)
        peripherals = get_external_peripherals()
        if peripherals:
            for peripheral in peripherals:
                self.devices_peripheral_menu["menu"].add_command(label=peripheral["type"], command=lambda value=peripheral["type"]: self.devices_peripheral_entry.set(value))
            self.devices_peripheral_entry.set(peripherals[0]["type"])
        else:
            self.devices_peripheral_entry.set("")

    """
    Update device's device assignation menu in graphical mode.
    """

    def gui_update_devices_device_menu(self):
        self.devices_device_menu["menu"].delete(0, END)
        devices = get_devices()
        if devices:
            for device in devices:
                self.devices_device_menu["menu"].add_command(label=(device["room"] + " (" + device["position"] + ")"), command=lambda value=(device["room"], device["position"]): self.devices_device_entry.set(value))
            self.devices_device_entry.set((devices[0]["room"], devices[0]["position"]))
        else:
            self.devices_device_entry.set("")

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
            self.roles_assignment_role_entry.set("")

    """
    Update commands's device menu in graphical mode.
    """

    def gui_update_commands_device_menu(self):
        self.commands_device_menu["menu"].delete(0, END)
        devices = get_devices()
        if devices:
            for device in devices:
                self.commands_device_menu["menu"].add_command(label=(device["room"] + " (" + device["position"] + ")"), command=lambda value=(device["room"], device["position"]): (self.commands_device_entry.set(value), Config.gui_update_commands_peripheral_menu(self)))
            self.commands_device_entry.set((devices[0]["room"], devices[0]["position"]))
        else:
            self.commands_device_entry.set("")

    """
    Update commands's peripheral menu in graphical mode.
    """

    def gui_update_commands_peripheral_menu(self):
        self.commands_peripheral_menu["menu"].delete(0, END)
        peripherals = get_device_peripherals(literal_eval(self.commands_device_entry.get())[0] if self.commands_device_entry.get() else self.commands_device_entry.get(), literal_eval(self.commands_device_entry.get())[1] if self.commands_device_entry.get() else self.commands_device_entry.get())
        if peripherals:
            for peripheral in peripherals:
                self.commands_peripheral_menu["menu"].add_command(label=peripheral, command=lambda value=peripheral: (self.commands_peripheral_entry.set(value), Config.gui_update_commands_subtype_menu(self), Config.gui_update_commands_action_menu(self)))
            self.commands_peripheral_entry.set(peripherals[0])
        else:
            self.commands_peripheral_entry.set("")

    """
    Update commands's subtype menu in graphical mode.
    """

    def gui_update_commands_subtype_menu(self):
        self.commands_subtype_menu["menu"].delete(0, END)
        actions = get_peripheral_subtypes(self.commands_peripheral_entry.get())
        if actions:
            for action in actions:
                self.commands_subtype_menu["menu"].add_command(label=action, command=lambda value=action: self.commands_subtype_entry.set(value))
            self.commands_subtype_entry.set(actions[0])
        else:
            self.commands_subtype_entry.set("")

    """
    Update commands's action menu in graphical mode.
    """

    def gui_update_commands_action_menu(self):
        self.commands_action_menu["menu"].delete(0, END)
        actions = get_peripheral_actions(self.commands_peripheral_entry.get())
        if actions:
            for action in actions:
                self.commands_action_menu["menu"].add_command(label=action, command=lambda value=action: self.commands_action_entry.set(value))
            self.commands_action_entry.set(actions[0])
        else:
            self.commands_action_entry.set("")

"""
Main.
"""

if __name__ == "__main__":
    try:
        languages = get_installed_languages()
        if not languages:
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}No languages found{DEFAULT}")
            exit()
        default_language = get_default_language()
        if not default_language:
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}No default language found{DEFAULT}")
            exit()
        print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Starting settings...{DEFAULT}")
        Config().mainloop()
    except KeyboardInterrupt:
        pass
    print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Exiting settings...{DEFAULT}")
    exit()
