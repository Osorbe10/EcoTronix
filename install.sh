#!/bin/bash

# Command line output color

RED="\e[1;31m"
GREEN="\e[1;32m"
YELLOW="\e[1;33m"
BLUE="\e[1;34m"
END="\e[0m"

# Trap CTRL + C

function control_c {
    echo -ne "${YELLOW}[${END}*${YELLOW}]${END} ${BLUE}Cancelling installation...${END}\n"
    exit
}

trap control_c INT

# Checks that the installation has superuser permissions

if [[ $(id -u) -ne 0 ]]; then
    echo -ne "${RED}[${END}*${RED}]${END} ${BLUE}Run it as root${END}\n"
    exit
fi

# Checks that the camera is valid

eval $(vcgencmd get_camera | cut -d "," -f 1);

if [[ ${supported} -ne 1 || ${detected} -ne 1 ]]; then
    echo -ne "${RED}[${END}*${RED}]${END} ${BLUE}Enable camera or check that is properly connected${END}\n"
    echo -ne "${BLUE}(1) --> sudo raspi-config${END}\n"
    echo -ne "${BLUE}(2) ----> Interface Options${END}\n"
    echo -ne "${BLUE}(3) ------> Legacy Camera${END}\n"
    echo -ne "${BLUE}(4) --------> Finish${END}\n"
    echo -ne "${BLUE}(5) ----------> Reboot${END}\n"
    exit
fi

# apt dependencies

function install_apt_dependencies {
    apt_dependencies=(espeak jq libatlas-base-dev python3.9 python3-opencv python3-pip python3-tk tar)
    for dependence in ${apt_dependencies[@]}; do
        dpkg -s ${dependence} >/dev/null 2>&1
        if [[ $? -ne 0 ]]; then
            echo -ne "${YELLOW}[${END}*${YELLOW}]${END} ${BLUE}Installing ${dependence}...${END}\n"
            sudo apt-get install -y ${dependence} >/dev/null 2>&1
            if [[ $? -ne 0 ]]; then
                echo -ne "${RED}[${END}-${RED}]${END} ${BLUE}${dependence} could not be installed${END}\n"
                exit
            fi
            echo -ne "${GREEN}[${END}+${GREEN}]${END} ${BLUE}${dependence} is now installed${END}\n"
        else
            echo -ne "${GREEN}[${END}+${GREEN}]${END} ${BLUE}${dependence} already installed${END}\n"
        fi
    done
}

# pip dependencies

function install_pip_dependencies {
    pip_dependencies=(chime face-recognition pocketsphinx)
    for dependence in ${pip_dependencies[@]}; do
        pip3 list | grep -F "${dependence}" >/dev/null 2>&1
        if [[ $? -ne 0 ]]; then
            echo -ne "${YELLOW}[${END}*${YELLOW}]${END} ${BLUE}Installing ${dependence}...${END}\n"
            sudo pip3 install ${dependence} >/dev/null 2>&1
            if [[ $? -ne 0 ]]; then
                echo -ne "${RED}[${END}-${RED}]${END} ${BLUE}${dependence} could not be installed${END}\n"
                exit
            fi
            echo -ne "${GREEN}[${END}+${GREEN}]${END} ${BLUE}${dependence} is now installed${END}\n"
        else
            echo -ne "${GREEN}[${END}+${GREEN}]${END} ${BLUE}${dependence} already installed${END}\n"
        fi
    done
}

# dlib dependence

function install_dlib_dependence {
    pip3 list | grep -F "dlib" >/dev/null 2>&1
    if [[ $? -ne 0 ]]; then
        echo -ne "${YELLOW}[${END}*${YELLOW}]${END} ${BLUE}Installing dlib...${END}\n"
        desired_swap_size=1024
        actual_swap_size=$(cat /etc/dphys-swapfile | grep "CONF_SWAPSIZE" | cut -d "=" -f 2)
        echo -ne "${YELLOW}[${END}*${YELLOW}]${END} ${BLUE}Setting swap size to ${desired_swap_size} MB...${END}\n"
        sudo sed -i "s/${actual_swap_size}/${desired_swap_size}/" /etc/dphys-swapfile
        sudo /etc/init.d/dphys-swapfile restart >/dev/null 2>&1
        mkdir -p dlib
        git clone -b "v19.6" --single-branch https://github.com/davisking/dlib.git dlib/ >/dev/null 2>&1
        cd ./dlib
        sudo python3 setup.py install --compiler-flags "-mfpu=neon" >/dev/null 2>&1
        cd ..
        sudo rm -rf dlib
        echo -ne "${YELLOW}[${END}*${YELLOW}]${END} ${BLUE}Restoring swap size to ${actual_swap_size} MB...${END}\n"
        sudo sed -i "s/${desired_swap_size}/${actual_swap_size}/" /etc/dphys-swapfile
        sudo /etc/init.d/dphys-swapfile restart >/dev/null 2>&1
        if [[ $? -ne 0 ]]; then
            echo -ne "${RED}[${END}-${RED}]${END} ${BLUE}dlib could not be installed${END}\n"
            exit
        fi
        echo -ne "${GREEN}[${END}+${GREEN}]${END} ${BLUE}dlib is now installed${END}\n"
    else
        echo -ne "${GREEN}[${END}+${GREEN}]${END} ${BLUE}dlib already installed${END}\n"
    fi
}

# Language packages

function install_es-es_language {
    languages_path=$1
    package=$2
    spanish=(cmusphinx-es-5.2.tar.gz es.dict)
    sudo mkdir ${languages_path}/${package}
    for file in ${spanish[@]}; do
        sudo wget -P ${languages_path}/${package} "https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/Spanish/${file}" >/dev/null 2>&1
        if [[ "${file}" =~ \.tar.gz$ ]]; then
            sudo tar -xvf ${languages_path}/${package}/${file} -C ${languages_path}/${package} >/dev/null 2>&1
            sudo rm ${languages_path}/${package}/${file}
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
    languages_path=$(python3 -c "from pocketsphinx import get_model_path; print(get_model_path())")
    echo -ne "${YELLOW}Available speech recognition language (X = installed): ${END}\n"
    for (( i=0; i<${#languages[@]}; i++ )); do
        if [[ -d "${languages_path}/${languages[${i}]}" ]]; then
            echo -ne "${YELLOW}[${GREEN}X${YELLOW}]${END} ${YELLOW}${languages[${i}]}${END}\n"
        else
            echo -ne "${YELLOW}[${GREEN}$i${END}${YELLOW}]${END} ${YELLOW}${languages[${i}]}${END}\n"
        fi
    done
    if ! [[ -f "${languages_path}/${languages[0]}/${languages[0]}.list" ]]; then
        sudo touch ${languages_path}/${languages[0]}/${languages[0]}.list
        jq --arg language "${languages[0]}" --arg hmm "${language_files[0,${hmm_row}]}" --arg dic "${language_files[0,${dic_row}]}" --arg kws "${language_files[0,${kws_row}]}" '.languages += [{"language": $language, "hmm": $hmm, "dic": $dic, "kws": $kws, "phrases": []}]' config.json > tmp.json && mv tmp.json config.json
    fi
    echo -ne "${YELLOW}Enter the numbers of the languages you want to install (separated by a space): ${END}"
    read selected_languages
    for i in ${selected_languages}; do
        if ! [[ -d "${languages_path}/${languages[${i}]}" ]]; then
            echo -ne "${YELLOW}[${END}*${YELLOW}]${END} ${BLUE}Installing ${languages[${i}]}...${END}\n"
            if [[ "${languages[${i}]}" == "es-es" ]]; then
                install_es-es_language ${languages_path} ${languages[${i}]}
            fi
            sudo touch ${languages_path}/${languages[${i}]}/${languages[${i}]}.list
            jq --arg language "${languages[${i}]}" --arg hmm "${language_files[${i},${hmm_row}]}" --arg dic "${language_files[${i},${dic_row}]}" --arg kws "${language_files[${i},${kws_row}]}" '.languages += [{"language": $language, "hmm": $hmm, "dic": $dic, "kws": $kws, "phrases": []}]' config.json > tmp.json && mv tmp.json config.json
            echo -ne "${GREEN}[${END}+${GREEN}]${END} ${BLUE}${languages[${i}]} is now installed${END}\n"
        fi
    done
    sudo chown $SUDO_USER:$SUDO_USER config.json
}

# Respberry Pi environment

function pi_environment {
    echo -ne "${YELLOW}[${END}*${YELLOW}]${END} ${BLUE}Preparing Raspberry Pi environment...${END}\n"
    if ! [[ -d "Faces/Encoded" ]]; then
        mkdir -p Faces/Encoded
        sudo chown -R $SUDO_USER:$SUDO_USER Faces
    fi
    sudo chmod +x config.py start.py
}

# Start installation

install_apt_dependencies
install_dlib_dependence
install_pip_dependencies
install_language_packages
pi_environment

# Finish installation

echo -ne "${GREEN}[${END}+${GREEN}]${END} ${BLUE}Installation completed${END}\n"
