#!/usr/bin/env python3

from chime import info
from config import BLUE, CONFIG_FILE, CONFIG_PATH, DEFAULT, ENCODED_FACES_EXTENSION, ENCODED_FACES_PATH, GREEN, RED, YELLOW
from contextlib import contextmanager
from cv2 import CAP_V4L2, resize, VideoCapture
from face_recognition import compare_faces, face_distance, face_encodings, face_locations
from json import load as json_load
from numpy import argmin, load as numpy_load
from os import devnull, path
from pyaudio import paInt16, PyAudio
from pocketsphinx import Config, Decoder, get_model_path
from subprocess import Popen
from threading import Event, Thread


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
Check if user is allowed to run command.
@param user: User
@param command: Command
@returns: True if user is allowed to run command. False if not
"""


def has_privileges(user, command):
    user_roles = []
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = json_load(config_file)
        for role in config["roles"]:
            if user in role["users"]:
                user_roles.append(role["role"])
        for _command in config["commands"]:
            if command == _command["command"]:
                for role in _command["roles"]:
                    if role in user_roles:
                        return True
    return False


"""
Launch desired user action.
@param phrase: Phrase
@param language: Phrase language
@param user_name: User name
"""


def action(phrase, language, user_name):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = json_load(config_file)
        for _language in config["languages"]:
            if language == _language["language"]:
                for _phrase in _language["phrases"]:
                    if phrase in _phrase["phrases"]:
                        command = _phrase["command"]
                        response = _phrase["response"]
                        if has_privileges(user_name, command):
                            info()
                            espeak = f"espeak -s 150 \"{response}\" -v {language} >{devnull} 2>&1"
                            Popen(command, shell=True)
                            Popen(espeak, shell=True)
                            print(
                                f"{GREEN}[{DEFAULT}+{GREEN}]{DEFAULT} {BLUE}Launched: {command}{DEFAULT}")
                        else:
                            print(
                                f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Not allowed to launch command{DEFAULT}")


"""
Launch speech recognition.
@param user_name: User name
@param language: Language
@param hmm_path: Hidden Markov Model path
@param dic_path: Dictionary path
@param kws_path: Keyword Spotting path
@param stop: Stop event
"""


def speech(user_name, language, hmm_path, dic_path, kws_path, stop):
    language_path = path.join(get_model_path(), language)
    config = Config(lm=None, hmm=path.join(language_path, hmm_path), dict=path.join(
        language_path, dic_path), kws=path.join(language_path, kws_path), logfn=devnull)
    decoder = Decoder(config)
    decoder.start_utt()
    with alsa_error():
        audio = PyAudio()
    stream = audio.open(format=paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=1024)
    print(
        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Listening {language} speech...{DEFAULT}")
    while not stop.is_set():
        buf = stream.read(1024)
        if buf:
            decoder.process_raw(buf, False, False)
            if decoder.hyp() is not None:
                phrase = decoder.hyp().hypstr.strip()
                print(
                    f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}You said: {DEFAULT}{phrase}")
                action(phrase, language, user_name)
                decoder.end_utt()
                decoder.start_utt()
        else:
            print(
                f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Cannot process audio...{DEFAULT}")
            break
    print(
        f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Stopping {language} speech...{DEFAULT}")
    decoder.end_utt()
    stream.close()


"""
Returns users data.
@returns: Encoded face, name and language for each user. False if there are no users
"""


def get_users():
    encoded_faces, names, languages = [], [], []
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = json_load(config_file)
        for user in config["users"]:
            names.append(user["name"])
            languages.append(user["language"])
            encoded_faces.append(numpy_load(
                ENCODED_FACES_PATH + user["face"] + ENCODED_FACES_EXTENSION))
        if len(names) == 0:
            print(
                f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}No users found{DEFAULT}")
            return False
    return (encoded_faces, names, languages)


"""
Returns language data.
@param language: Language package
@returns: Hidden Markov Model, dictionary and keywords paths. False if language not exists
"""


def get_language_paths(language):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = json_load(config_file)
        for _language in config["languages"]:
            if language == _language["language"]:
                return (_language["hmm"], _language["dic"], _language["kws"])
    print(f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Non existing language{DEFAULT}")
    return False


if __name__ == "__main__":
    try:
        print(
            f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Starting EcoTronix...{DEFAULT}")
        users = get_users()
        if users:
            encoded_faces, names, languages = users
            process_frame = True
            user_name = ""
            stop = Event()
            t_speech = None
            camera = VideoCapture(CAP_V4L2)
            print(
                f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Reading faces...{DEFAULT}")
            while True:
                returned, frame = camera.read()
                if not returned:
                    camera.release()
                    print(
                        f"{RED}[{DEFAULT}-{RED}]{DEFAULT} {BLUE}Unable to read camera{DEFAULT}")
                    break
                if process_frame:
                    rgb_small_frame = resize(frame, (0, 0), fx=0.25, fy=0.25)[
                        :, :, ::-1]
                    found_faces = face_locations(rgb_small_frame)
                    encoded_found_faces = face_encodings(
                        rgb_small_frame, found_faces)
                    for encoded_face in encoded_found_faces:
                        best_match_index = argmin(
                            face_distance(encoded_faces, encoded_face))
                        if compare_faces(encoded_faces, encoded_face)[best_match_index]:
                            name = names[best_match_index]
                            if user_name != name:
                                print(
                                    f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Loading {name} profile...{DEFAULT}")
                                user_name = name
                                language = languages[best_match_index]
                                hmm_path, dic_path, kws_path = get_language_paths(
                                    language)
                                if t_speech is not None:
                                    stop.set()
                                    t_speech.join()
                                    stop.clear()
                                t_speech = Thread(target=speech, args=(
                                    user_name, language, hmm_path, dic_path, kws_path, stop))
                                t_speech.start()
                process_frame = not process_frame
        print(
            f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Finishing EcoTronix...{DEFAULT}")
    except KeyboardInterrupt:
        if t_speech is not None:
            stop.set()
            t_speech.join()
        print(
            f"{YELLOW}[{DEFAULT}*{YELLOW}]{DEFAULT} {BLUE}Exiting EcoTronix...{DEFAULT}")
