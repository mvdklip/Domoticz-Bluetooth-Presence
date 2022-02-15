# Domoticz-Bluetooth-Presence
Domoticz plugin to detect if a given bluetooth MAC address is within reach

Tested with Python version 3.8, Domoticz version 2020.2

## Prerequisites

- Bluetooth MAC address of device to be used for presence detection;
- Python 'bluetooth' (python3-bluez) library installed.

## Installation

Assuming that domoticz directory is installed in your home directory.

```bash
cd ~/domoticz/plugins
git clone https://github.com/mvdklip/Domoticz-Bluetooth-Presence
sudo apt-get install python3-bluez
# restart domoticz:
sudo /etc/init.d/domoticz.sh restart
```
In the web UI, navigate to the Hardware page and add an entry of type "Bluetooth Presence".

Make sure to (temporarily) enable 'Accept new Hardware Devices' in System Settings so that the plugin can add devices.

Afterwards navigate to the Devices page and enable the newly created devices.

## Updating

Like other plugins, in the Domoticz-Bluetooth-Presence directory:
```bash
git pull
sudo /etc/init.d/domoticz.sh restart
```

## Parameters

| Parameter | Value |
| :--- | :--- |
| **Bluetooth MAC Address** | Bluetooth MAC address of the device |
| **Cooldown in seconds** | Amount of time to pass before marking device as non-present |
| **Debug** | Configures debug logging |
