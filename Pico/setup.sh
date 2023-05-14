#!/bin/bash

# Command line output color

RED="\e[1;31m"
GREEN="\e[1;32m"
YELLOW="\e[1;33m"
BLUE="\e[1;34m"
DEFAULT="\e[0m"

# Pico directory

DIR=$(dirname "$(readlink -f "$0")")

# Trap CTRL + C

function control_c {
    echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Cancelling installation...${DEFAULT}\n"
    exit 1
}

trap control_c INT

# Setup Raspberry Pi Pico W

pico_path="/media/${USER}/RPI-RP2/"
if ! [[ -d "${pico_path}" ]]; then
    echo -ne "${YELLOW}Connect your Raspberry Pi Pico W to the Raspberry Pi via the bootsel button...${DEFAULT}\n"
    while ! [[ -d "$pico_path" ]]; do
        :
    done
fi
ls /dev/tty* > ${DIR}/old.tmp
echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Installing Micropython firmware...${DEFAULT}\n"
sudo cp ${DIR}/micropython.uf2 ${pico_path}
echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}Micropython firmware installed${DEFAULT}\n"
ls /dev/tty* > ${DIR}/new.tmp
while [[ "$(diff "${DIR}/old.tmp" "${DIR}/new.tmp")" == "" ]]; do
    ls /dev/tty* > ${DIR}/new.tmp
done
tty=$(diff ${DIR}/old.tmp ${DIR}/new.tmp | tail -n 1 | cut -d " " -f 2)
rm ${DIR}/old.tmp ${DIR}/new.tmp
echo -ne "${YELLOW}[${DEFAULT}*${YELLOW}]${DEFAULT} ${BLUE}Copying codes...${DEFAULT}\n"
rshell --buffer-size 512 -p ${tty} rm -r /pyboard/* >/dev/null 2>&1
rshell --buffer-size 512 -p ${tty} cp ${DIR}/Codes/main.py /pyboard >/dev/null 2>&1
rshell --buffer-size 512 -p ${tty} cp ${DIR}/Codes/config.json /pyboard >/dev/null 2>&1
rshell --buffer-size 512 -p ${tty} cp -r ${DIR}/Codes/umqtt /pyboard >/dev/null 2>&1
echo -ne "${GREEN}[${DEFAULT}+${GREEN}]${DEFAULT} ${BLUE}Codes copied${DEFAULT}\n"

exit 0
