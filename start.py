#!/usr/bin/env python3

from chime import info, success, warning
from Common.commands import get_command
from Common.constants import BLUE, COMMAND_TIMEOUT, DEFAULT, ENCODED_FACES_EXTENSION, ENCODED_FACES_PATH, GREEN, LANGUAGES_PATH, RED, YELLOW
from Common.devices import get_devices
from Common.general import get_mqtt_user, get_mqtt_password
from Common.languages import get_default_language, get_default_language_paths
from Common.peripherals import get_device_peripherals, get_peripheral_actions, get_peripheral_subtypes
from Common.users import get_users, get_user_permissions
from contextlib import contextmanager
from cv2 import CAP_V4L2, resize, VideoCapture
from face_recognition import compare_faces, face_distance, face_encodings, face_locations
from numpy import argmin, load as numpy_load
from os import devnull, path
from paho.mqtt.client import Client, MQTTv5
from pocketsphinx import Config, Decoder
from pyaudio import paInt16, PyAudio
from socket import gethostname
from subprocess import Popen
from threading import Event, Lock, Thread
from time import sleep, time

"""
Removes alsa lib irrelevant errors.
"""

@contextmanager
def alsa_error():
    import os
    import sys
    dev_null = os.open(devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(dev_null, 2)
    os.close(dev_null)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

"""
Pending commands structure.
"""

class PendingCommands:

    """
    Constructs pending commands structure.
    """

    def __init__(self):
        self.pending_commands = []
        self.lock = Lock()
        self.t_pending_commands = Thread(target=self.remove_timed_out)
        self.t_pending_commands.daemon = True
        self.t_pending_commands.start()

    """
    Add a pending command.
    @param config_command: Command
    @param language: Language
    """

    def append(self, config_command, language):
        with self.lock:
            self.pending_commands.append((config_command, language, time()))

    """
    Get a pending command.
    @param index: Index
    @returns: A tuple with command and language
    """

    def get(self, index):
        with self.lock:
            return (self.pending_commands[index][0], self.pending_commands[index][1])

    """
    Delete a pending command.
    @param index: Index
    """

    def remove(self, index):
        with self.lock:
            del self.pending_commands[index]

    """
    Count pending command.
    @returns: Pending command count
    """

    def len(self):
        with self.lock:
            return len(self.pending_commands)

    """
    Delete timed out pending command.
    """

    def remove_timed_out(self):
        while True:
            sleep(COMMAND_TIMEOUT)
            with self.lock:
                current_time = time()
                self.pending_commands = [(config_command, language, timestamp) for config_command, language, timestamp in self.pending_commands if current_time - timestamp < COMMAND_TIMEOUT]

"""
Executes a command.
@param config_command: Command
@param language: Language
"""

def execute(config_command, language):
    global client
    if "command" in config_command:
        command = config_command["command"]
        response = config_command["response"]
        Popen(command, shell=True)
        Popen(f"espeak -s 150 \"{response}\" -v {language} >{devnull} 2>&1", shell=True)
        print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Executed: {command}{DEFAULT}")
    elif "peripheral" in config_command and "subtype" in config_command and "action" in config_command and "room" in config_command and "position" in config_command:
        peripheral = config_command["peripheral"]
        subtype = config_command["subtype"]
        action = config_command["action"]
        room = config_command["room"]
        position = config_command["position"]
        response = config_command["response"]
        hierarchy = path.join(room.lower().replace(" ", "_"), position.lower().replace(" ", "_"), peripheral.lower().replace(" ", "_"))
        if subtype:
            hierarchy = path.join(hierarchy, subtype.lower().replace(" ", "_"))
        client.publish(hierarchy, payload=action, qos=1)
        Popen(f"espeak -s 150 \"{response}\" -v {language} >{devnull} 2>&1", shell=True)
        print(f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Executed: " + hierarchy + (" " + action if action else "") + f"{DEFAULT}")

"""
Executes pending commands user is allowed to.
@param name: User name
"""

def execute_pending(name):
    permissions = get_user_permissions(name)
    if permissions and (permissions["privileged"] or not permissions["age_restriction"]):
            for index in range(pending_commands.len()):
                pending_command = pending_commands.get(index - 1)
                if user_allowed(pending_command[0]["age_restriction"], pending_command[0]["privileged"], permissions["age_restriction"], permissions["privileged"]):
                    pending_commands.remove(index - 1)
                    info()
                    execute(pending_command[0], pending_command[1])

"""
Checks if a command is allowed.
@param command: Command
@returns: True if command is allowed. False if not
"""

def permissions(config_command):
    if not config_command["age_restriction"] and not config_command["privileged"]:
        return True
    return False

"""
Checks if a user is allowed to execute a command.
@param command_age_restriction: Command age restriction
@param command_privileged: Command privileged
@param user_age_restriction: User age restriction
@param user_privileged: User privileged
@returns: True if user is allowed. False if not
"""

def user_allowed(command_age_restriction, command_privileged, user_age_restriction, user_privileged):
    if (command_age_restriction and not user_age_restriction and not command_privileged) or (command_privileged and user_privileged and not command_age_restriction) or (command_age_restriction and not user_age_restriction and command_privileged and user_privileged):
        return True
    return False

"""
Launch desired action if is allowed.
@param phrase: Phrase
@param language: Phrase language
"""

def action(phrase, language):
    config_command = get_command(phrase, language)
    if not config_command:
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Unexpected phrase recognized{DEFAULT}")
        return
    if permissions(config_command):
        info()
        execute(config_command, language)
    else:
        warning()
        pending_commands.append(config_command, language)
        print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Will be executed when it has sufficient permissions{DEFAULT}")

"""
Runs speech recognition until stop event is set.
@param stop: Stop event
"""

def speech_recognition(stop):
    hmm_path, dic_path, kws_path = language_paths
    config = Config(lm=None, hmm=path.join(LANGUAGES_PATH, language, hmm_path), dict=path.join(LANGUAGES_PATH, language, dic_path), kws=path.join(LANGUAGES_PATH, language, kws_path), logfn=devnull)
    decoder = Decoder(config)
    decoder.start_utt()
    with alsa_error():
        audio = PyAudio()
    stream = audio.open(format=paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Listening {language} speech...{DEFAULT}")
    while not stop.is_set():
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
            if decoder.hyp() is not None:
                phrase = decoder.hyp().hypstr.strip()
                print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}You said: {DEFAULT}{phrase}")
                action(phrase, language)
                decoder.end_utt()
                decoder.start_utt()
        else:
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Cannot process audio...{DEFAULT}")
            break
    decoder.end_utt()
    stream.close()

"""
Runs face recognition until stop event is set.
@param stop: Stop event
"""

def face_recognition(stop):
    names, encoded_faces = [], []
    for user in users:
        names.append(user["name"])
        encoded_faces.append(numpy_load(ENCODED_FACES_PATH + user["face"] + ENCODED_FACES_EXTENSION))
    process_frame = True
    last_user = ""
    camera = VideoCapture(CAP_V4L2)
    print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Reading faces...{DEFAULT}")
    while not stop.is_set():
        returned, frame = camera.read()
        if not returned:
            camera.release()
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Unable to read camera{DEFAULT}")
            break
        if process_frame:
            rgb_small_frame = resize(frame, (0, 0), fx=0.25, fy=0.25)[:, :, ::-1]
            found_faces = face_locations(rgb_small_frame)
            encoded_found_faces = face_encodings(rgb_small_frame, found_faces)
            for encoded_face in encoded_found_faces:
                best_match_index = argmin(face_distance(encoded_faces, encoded_face))
                if compare_faces(encoded_faces, encoded_face)[best_match_index]:
                    name = names[best_match_index]
                    if last_user != name:
                        success()
                        print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Loading {name} profile...{DEFAULT}")
                        last_user = name
                        # TODO: Launch every action associated with the user
                    execute_pending(name)
        process_frame = not process_frame
    camera.release()

"""
Prints sensor value when requested.
"""

def on_message(client, userdata, message):
    print(f"{message.topic}: {message.payload.decode()}")

"""
Subscribes to installed devices peripherals with any sensor function.
@param client: MQTT client
"""

def subscribing(client):
    for device in get_devices():
        if device["installed"]:
            device_path = path.join(device["room"].lower().replace(" ", "_"), device["position"].lower().replace(" ", "_"))
            for peripheral in get_device_peripherals(device["room"], device["position"]):
                if "get" in get_peripheral_actions(peripheral):
                    peripheral_path = path.join(device_path, peripheral.lower().replace(" ", "_"))
                    subtypes = get_peripheral_subtypes(peripheral)
                    if subtypes:
                        for subtype in subtypes:
                            client.subscribe(path.join(peripheral_path, subtype.lower().replace(" ", "_"), "get"), qos=1)
                            print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Suscribed to " + path.join(peripheral_path, subtype.lower().replace(" ", "_"), "get") + f"{DEFAULT}")
                    else:
                        client.subscribe(path.join(peripheral_path, "get"), qos=1)
                        print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Suscribed to " + path.join(peripheral_path, "get") + f"{DEFAULT}")

"""
Connects to MQTT broker.
@param client: MQTT client
@returns: True if MQTT client is connected. False if not
"""

def start_mqtt():
    global client
    client = Client(gethostname(), protocol=MQTTv5)
    try:   
        client.username_pw_set(get_mqtt_user(), get_mqtt_password())
        client.connect("127.0.0.1", 1883)
    except ConnectionRefusedError:
        return False
    client.on_message = on_message
    subscribing(client)
    client.loop_start()
    return True

"""
Main.
"""

if __name__ == "__main__":
    try:
        users = get_users()
        if not users:
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}No users found{DEFAULT}")
            exit()
        language = get_default_language()
        language_paths = get_default_language_paths()
        if not language or not language_paths:
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}No languages found{DEFAULT}")
            exit()
        print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Starting EcoTronix...{DEFAULT}")
        client, t_face, t_speech, stop = None, None, None, None
        if not start_mqtt():
            print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Cannot connect to MQTT broker{DEFAULT}")
            exit()
        pending_commands = PendingCommands()
        stop = Event()
        t_face = Thread(target=face_recognition, args=(stop,))
        t_speech = Thread(target=speech_recognition, args=(stop,))
        t_face.start()
        t_speech.start()
        stop.wait()
    except KeyboardInterrupt:
        if stop is not None:
            stop.set()
        if t_speech is not None:
            t_speech.join()
        if t_face is not None:
            t_face.join()
        if client is not None:
            client.disconnect()
    print(f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Exiting EcoTronix...{DEFAULT}")
    exit()
