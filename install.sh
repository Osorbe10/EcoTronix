#!/bin/bash

# Command line output color

RED="\e[1;31m"
GREEN="\e[1;32m"
YELLOW="\e[1;33m"
BLUE="\e[1;34m"
DEFAULT="\e[0m"

# Trap CTRL + C

function control_c {
    echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Cancelling installation...${DEFAULT}\n"
    exit
}

trap control_c INT

# Checks that the installation has superuser permissions

if [[ $(id -u) -ne 0 ]]; then
    echo -ne "${RED}[${DEFAULT}-${RED}]${DEFAULT} ${BLUE}Run it as root${DEFAULT}\n"
    exit
fi

# Checks that the camera is valid

eval $(vcgencmd get_camera | cut -d "," -f 1);

if [[ ${supported} -ne 1 || ${detected} -ne 1 ]]; then
    echo -ne "${RED}[${DEFAULT}-${RED}]${DEFAULT} ${BLUE}Enable camera or check that is properly connected${DEFAULT}\n"
    echo -ne "${BLUE}(1) --> sudo raspi-config${DEFAULT}\n"
    echo -ne "${BLUE}(2) ----> Interface Options${DEFAULT}\n"
    echo -ne "${BLUE}(3) ------> Legacy Camera${DEFAULT}\n"
    echo -ne "${BLUE}(4) --------> Finish${DEFAULT}\n"
    echo -ne "${BLUE}(5) ----------> Reboot${DEFAULT}\n"
    exit
fi

# APT dependencies

function install_apt_dependencies {
    apt_dependencies=(espeak jq libatlas-base-dev mosquitto python3.9 python3-opencv python3-pip python3-tk tar)
    for dependence in ${apt_dependencies[@]}; do
        dpkg -s ${dependence} >/dev/null 2>&1
        if [[ $? -ne 0 ]]; then
            echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Installing ${dependence}...${DEFAULT}\n"
            sudo apt install -y ${dependence} >/dev/null 2>&1
            if [[ $? -ne 0 ]]; then
                echo -ne "${RED}[${DEFAULT}-${RED}]${DEFAULT} ${BLUE}${dependence} could not be installed${DEFAULT}\n"
                exit
            fi
            echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}${dependence} is now installed${DEFAULT}\n"
        else
            echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}${dependence} already installed${DEFAULT}\n"
        fi
    done
}

# PIP dependencies

function install_pip_dependencies {
    pip_dependencies=(chime face-recognition paho-mqtt pocketsphinx PyAudio rshell)
    for dependence in ${pip_dependencies[@]}; do
        pip3 list | grep -F "${dependence}" >/dev/null 2>&1
        if [[ $? -ne 0 ]]; then
            echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Installing ${dependence}...${DEFAULT}\n"
            sudo pip3 install ${dependence} >/dev/null 2>&1
            if [[ $? -ne 0 ]]; then
                echo -ne "${RED}[${DEFAULT}-${RED}]${DEFAULT} ${BLUE}${dependence} could not be installed${DEFAULT}\n"
                exit
            fi
            echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}${dependence} is now installed${DEFAULT}\n"
        else
            echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}${dependence} already installed${DEFAULT}\n"
        fi
    done
}

# DLIB dependence

function install_dlib_dependence {
    pip3 list | grep -F "dlib" >/dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Installing dlib...${DEFAULT}\n"
        desired_swap_size=1024
        actual_swap_size=$(cat /etc/dphys-swapfile | grep "CONF_SWAPSIZE" | cut -d "=" -f 2)
        echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Setting swap size to ${desired_swap_size} MB...${DEFAULT}\n"
        sudo sed -i "s/${actual_swap_size}/${desired_swap_size}/" /etc/dphys-swapfile
        sudo /etc/init.d/dphys-swapfile restart >/dev/null 2>&1
        mkdir -p dlib
        git clone -b "v19.6" --single-branch https://github.com/davisking/dlib.git dlib/ >/dev/null 2>&1
        cd ./dlib
        sudo python3 setup.py install --compiler-flags "-mfpu=neon" >/dev/null 2>&1
        cd ..
        sudo rm -rf dlib
        echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Restoring swap size to ${actual_swap_size} MB...${DEFAULT}\n"
        sudo sed -i "s/${desired_swap_size}/${actual_swap_size}/" /etc/dphys-swapfile
        sudo /etc/init.d/dphys-swapfile restart >/dev/null 2>&1
        if [[ $? -ne 0 ]]; then
            echo -ne "${RED}[${DEFAULT}-${RED}]${DEFAULT} ${BLUE}dlib could not be installed${DEFAULT}\n"
            exit
        fi
        echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}dlib is now installed${DEFAULT}\n"
    else
        echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}dlib already installed${DEFAULT}\n"
    fi
}

# Language packages

function install_es-es_language {
    languages_path=$1
    package=$2
    files=(cmusphinx-es-5.2.tar.gz es.dict)
    mkdir ${languages_path}/${package}
    for file in ${files[@]}; do
        wget -P ${languages_path}/${package} "https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Spanish/${file}" >/dev/null 2>&1
        if [[ "${file}" =~ \.tar.gz$ ]]; then
            tar -xvf ${languages_path}/${package}/${file} -C ${languages_path}/${package} >/dev/null 2>&1
            rm ${languages_path}/${package}/${file}
        fi
    done
}

function install_language_packages {
    languages=("en-us" "es-es")
    hmm_row=0
    dic_row=1
    kws_row=2
    declare -A language_files
    language_files[0,${hmm_row}]="en-us"
    language_files[0,${dic_row}]="cmudict-en-us.dict"
    language_files[0,${kws_row}]="en-us.list"
    language_files[1,${hmm_row}]="cmusphinx-es-5.2/model_parameters/voxforge_es_sphinx.cd_ptm_4000"
    language_files[1,${dic_row}]="es.dict"
    language_files[1,${kws_row}]="es-es.list"
    languages_path="Languages"
    if ! [[ -d ${languages_path} ]]; then
        mkdir ${languages_path}
        cp -r $(python3 -c "from pocketsphinx import get_model_path; print(get_model_path())")/${languages[0]} ${languages_path}/${languages[0]}
    fi
    if ! [[ -f "${languages_path}/${languages[0]}/${languages[0]}.list" ]]; then
        touch ${languages_path}/${languages[0]}/${languages[0]}.list
        jq --arg language "${languages[0]}" --arg hmm "${language_files[0,${hmm_row}]}" --arg dic "${language_files[0,${dic_row}]}" --arg kws "${language_files[0,${kws_row}]}" '.languages += [{"language": $language, "hmm": $hmm, "dic": $dic, "kws": $kws}]' config.json > tmp.json && mv tmp.json config.json
        chown $SUDO_USER:$SUDO_USER config.json
        jq --arg language "${languages[0]}" '.general.default_language = $language' config.json > tmp.json && mv tmp.json config.json
        chown $SUDO_USER:$SUDO_USER config.json
    fi
    echo -ne "${YELLOW}Available speech recognition language (X = installed): ${DEFAULT}\n"
    for (( i=0; i<${#languages[@]}; i++ )); do
        if [[ -d "${languages_path}/${languages[${i}]}" ]]; then
            echo -ne "${YELLOW}[${BLUE}X${YELLOW}]${DEFAULT} ${YELLOW}${languages[${i}]}${DEFAULT}\n"
        else
            echo -ne "${YELLOW}[${BLUE}$i${DEFAULT}${YELLOW}]${DEFAULT} ${YELLOW}${languages[${i}]}${DEFAULT}\n"
        fi
    done
    echo -ne "${YELLOW}Enter the numbers of the languages you want to install (separated by a space): ${DEFAULT}"
    read selected_languages
    for i in ${selected_languages}; do
        if ! [[ -d "${languages_path}/${languages[${i}]}" ]]; then
            echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Installing ${languages[${i}]}...${DEFAULT}\n"
            if [[ "${languages[${i}]}" == "es-es" ]]; then
                install_es-es_language ${languages_path} ${languages[${i}]}
            fi
            touch ${languages_path}/${languages[${i}]}/${languages[${i}]}.list
            jq --arg language "${languages[${i}]}" --arg hmm "${language_files[${i},${hmm_row}]}" --arg dic "${language_files[${i},${dic_row}]}" --arg kws "${language_files[${i},${kws_row}]}" '.languages += [{"language": $language, "hmm": $hmm, "dic": $dic, "kws": $kws}]' config.json > tmp.json && mv tmp.json config.json
            chown $SUDO_USER:$SUDO_USER config.json
            echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}${languages[${i}]} is now installed${DEFAULT}\n"
        fi
    done
    chown -R $SUDO_USER:$SUDO_USER ${languages_path}
}

# Respberry Pi environment

function pi_environment {
    echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Preparing Raspberry Pi environment...${DEFAULT}\n"
    if ! [[ -d "Faces/Encoded" ]]; then
        mkdir -p Faces/Encoded
        chown -R $SUDO_USER:$SUDO_USER Faces
    fi
    chmod +x config.py start.py Pico/setup.sh
    if ! [[ -f "/etc/mosquitto/conf.d/EcoTronix.conf" ]]; then
        sudo touch /etc/mosquitto/conf.d/EcoTronix.conf
        sudo echo "allow_anonymous true" > /etc/mosquitto/conf.d/EcoTronix.conf
        sudo echo "listener 1883" >> /etc/mosquitto/conf.d/EcoTronix.conf
        sudo systemctl restart mosquitto.service
    fi
    echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}Raspberry Pi environment prepared${DEFAULT}\n"
}

# Finish installation

function finish {
    echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}Installation completed${DEFAULT}\n"
}

# Installation

install_apt_dependencies
install_dlib_dependence
install_pip_dependencies
install_language_packages
pi_environment
finish
