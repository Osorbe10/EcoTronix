# EcoTronix

Low Cost Interactive Home Automation Prototype

## Components

    Required

        - Raspberry Pi
        - Raspberry Pi Camera
        - Microphone [USB]

    Optional

        - Speaker [USB] or [MiniJack 3,5 mm]

## Installation

Open a terminal in the directory where you want to download the project and paste the following fragment:

```bash
sudo apt-get update && sudo apt-get upgrade -y && sudo apt autoremove -y
sudo apt-get install git -y
git clone https://github.com/Osorbe10/EcoTronix.git
cd EcoTronix
sudo chmod +x install.sh
sudo ./install.sh
```

Once the installation is finished, it is recommended to enter the settings to configure the system.

## Usage

To enter the settings just type the following command in the terminal:

```bash
sudo ./config.py
```

It's important never to modify configuration files directly. To do this, it's essential to use the above configuration program.

Once configured, to start the application type the following command in the terminal:

```bash
./start.py
```

## Compatibility

Tested on Raspbian GNU/Linux 11 (bullseye) for Raspberry Pi 3 Model B Rev 1.2 with a Raspberry Pi Camera Rev 1.3

To verify your Raspberry Pi model and OS, enter the following command in a terminal:

```bash
echo "Model:" $(cat /sys/firmware/devicetree/base/model | tr -d '\0')
echo "OS:" $(cat /etc/os-release | grep "PRETTY_NAME" | awk -F '=' '{print $2}' | tr -d '"')
```
