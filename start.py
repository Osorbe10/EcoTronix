#!/usr/bin/env python3

from chime import info
from config import CONFIG_FILE, CONFIG_PATH, ENCODED_FACES_PATH, ENCODED_FACES_EXTENSION
from cv2 import CAP_V4L2, resize, VideoCapture
from face_recognition import compare_faces, face_distance, face_encodings, face_locations
from json import load as json_load
from numpy import argmin, load as numpy_load
from os import path
from pocketsphinx import get_model_path, LiveSpeech
from subprocess import Popen
from threading import Condition, Lock, Thread

user_name, user_language, hmm_path, dic_path, kws_path = "", "", "", "", ""
actual_user = Condition(Lock())

"""
Launch desired user action.
@param phrase: Phrase
@param language: Phrase language
@returns: True if phrase is a valid action and can be launched. False otherwise
"""


def action(phrase, language):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = json_load(config_file)
        for _language in config["languages"]:
            if language == _language["language"]:
                for _phrase in _language["phrases"]:
                    if phrase in _phrase["phrases"]:
                        print("[+] Launched: " + _phrase["command"])
                        Popen(_phrase["command"], shell=True)
                        Popen(
                            "espeak -s 150 \"" + _phrase["response"] + "\" -v " + language + " >/dev/null 2>&1", shell=True)
                        return True
    return False


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
            print("[*] No users found")
            return False
    return (encoded_faces, names, languages)


"""
Returns language data.
@param language: Language package
@returns: Language and Hidden Markov Model and dictionary. False if language not exists
"""


def get_language(language):
    with open(CONFIG_PATH + CONFIG_FILE, "r") as config_file:
        config = json_load(config_file)
        for _language in config["languages"]:
            if language == _language["language"]:
                return (_language["hmm"], _language["dic"], _language["kws"])
    print("[-] Non existing language")
    return False


"""
Capture users faces through the camera and updates current user.
@param function: Thread functionality
@returns: False if there are no users or if camera is unabled to read
"""


def capture_face(function):
    print("[*] Starting " + function + "...")
    global user_name, user_language, hmm_path, dic_path, kws_path
    users = get_users()
    if not users:
        print("[*] Exiting " + function + "...")
        return False
    encoded_faces, names, languages = users
    process_frame = True
    camera = VideoCapture(CAP_V4L2)
    print("[*] " + function + " reading faces...")
    while True:
        returned, frame = camera.read()
        if not returned:
            camera.release()
            print("[-] Unable to read camera")
            print("[*] Exiting " + function + "...")
            return False
        if process_frame:
            rgb_small_frame = resize(frame, (0, 0), fx=0.25, fy=0.25)[
                :, :, ::-1]
            found_faces = face_locations(rgb_small_frame)
            encoded_found_faces = face_encodings(rgb_small_frame, found_faces)
            for encoded_face in encoded_found_faces:
                best_match_index = argmin(
                    face_distance(encoded_faces, encoded_face))
                if compare_faces(encoded_faces, encoded_face)[best_match_index]:
                    name = names[best_match_index]
                    if user_name != name:
                        actual_user.acquire()
                        user_language = languages[best_match_index]
                        hmm_path, dic_path, kws_path = get_language (user_language)
                        user_name = name
                        actual_user.notify_all()
                        actual_user.release()
                        print("[+] Welcome, " + name + "...")
        process_frame = not process_frame


"""
Capture users speech through the microphone and launch actions.
@param function: Thread functionality
@returns: False if there is no microphone available
"""


def capture_speech(function):
    global user_name, user_language, hmm_path, dic_path, kws_path
    model_path = get_model_path()
    print("[*] " + function + " waiting for an user face...")
    actual_user.acquire()
    while not user_name:
        actual_user.wait()
    print("[*] Starting " + function + "...")
    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        lm=False,
        hmm=path.join(model_path, user_language + "/" + hmm_path),
        dic=path.join(model_path, user_language + "/" + dic_path),
        kws=path.join(model_path, user_language + "/" + kws_path)
    )
    actual_user.release()
    for phrase in speech:
        info()
        if not action(str(phrase).rstrip(), user_language):
            print("[-] Invalid action")
    print("[*] Exiting " + function + "...")
    return False


"""
Launch face and speech recognition.
"""


def main():
    print("[*] Starting EcoTronix...")
    str_face_recognition = "face recognition"
    str_speech_recognition = "speech recognition"
    try:
        face_recognition = Thread(
            target=capture_face, daemon=True, args=(str_face_recognition, ))
        speech_recognition = Thread(
            target=capture_speech, daemon=True, args=(str_speech_recognition, ))
        print("[*] Launching " + str_face_recognition + "...")
        face_recognition.start()
        print("[*] Launching " + str_speech_recognition + "...")
        speech_recognition.start()
        while face_recognition.is_alive() and speech_recognition.is_alive():
            pass
        print("[*] Finishing EcoTronix...")
    except KeyboardInterrupt:
        print("[*] Exiting EcoTronix...")


if __name__ == "__main__":
    main()
