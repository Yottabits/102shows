## Why there is a manual instead of three bash commands 

102shows consists of two parts:
 - the **lightshow server**, which should run on a Raspberry Pi
   - it controls the LED strip via SPI
   - it listens for MQTT messages that tell it which show to start (and what the paramters for the show are)
 - the **UI**
   - it delivers a nice web interface
   - it sends the MQTT messages to the server

For the two elements to be able to communicate (via MQTT) you need an **MQTT broker**, for example *mosquitto*

All of these can run on the same Raspberry Pi but only the server has to.

***

# Installing 102shows

## MQTT broker
If you already have an MQTT broker in your network, you can use it. Else, install `mosquitto` via `sudo apt-get install mosquitto`. In any case, you will need the host, port (and maybe access credentials) of your MQTT broker for later.

## Server

### variant A: the simple way
In the folder you want to install 102shows in, run:

    wget -q -O 102s-setup.sh https://git.io/v1x1q; chmod +x 102s-setup.sh; ./102s-setup.sh; rm 102s-setup.sh
    
This will launch an assistant that will lead you through the installation process.

### variant B: the DIY all-manual way

#### 1. Prerequisites
You will need Python 3 with the following packages:
 - [coloredlogs](https://pypi.python.org/pypi/coloredlogs)
 - [orderedattrdict](https://pypi.python.org/pypi/orderedattrdict)
 - [paho-mqtt](https://pypi.python.org/pypi/paho-mqtt)

Install them with:
```
sudo apt-get update
sudo apt-get install python3 python3-pip
pip3 install paho-mqtt
```

#### 2. Getting the code
Download the latest release of 102shows as [tar](https://api.github.com/repos/Yottabits/102shows/tarball) or [zip](https://api.github.com/repos/Yottabits/102shows/zipball) and unpack it where you would like it to install.

#### 3. Configure the server
In the folder `server`, copy `config.example.yml` to `config.yml`, uncomment and fill out the sample setting directives in config.yml. The resulting file could look like [this](https://gist.github.com/sleiner/dd967b20d555e78f1d3d67b7aa49324a)

### Running the server
Run `python3 /path/to/102shows/server/server.py`


## Web UI

### 1. Prerequisites
The web UI depends on [Node-RED](https://nodered.org/) with the [dashboard](https://flows.nodered.org/node/node-red-dashboard) add-on. 

- Install Node-RED: (this is **not necessary** on Raspbian)
    - Install node.js (including npm): `sudo apt-get install nodejs` (not necessary on Raspbian)
    - Update npm: `sudo npm install npm@latest -g`
    - Install Node-RED: `sudo npm install -g node-red`
- Install the Node-RED dashboard add-on (**note that you have to uninstall any previous versions of node-red-contrib-ui etc. first**): `npm install node-red-dashboard`

### 2. Start Node-RED
Execute `node-red` on a console. The Node-RED administration interface should now be available on `http://localhost:1880`

**Raspbian tip: ** If you want Node-RED to automatically start on boot, execute: `sudo systemctl enable nodered.service`

### 3. Paste the 102shows UI in Node-RED
Copy the contents of [ui/nodered.json](https://raw.githubusercontent.com/Yottabits/102shows/stable/ui/nodered.json) into the clipboard.
Go to the Node-RED admin interface and in the main menu (upper right corner) choose *Import* >> *Clipboard* and paste the code you copied earlier into the window that is opening. Confirm with *Import*

You should now see the flow **LED control**

### 4. Configure the 102shows UI
In the upper left of **LED control** there is a node named **global settings**. Double-click on it to open it and modify the preferences in the code so that they match the settings in your server-side *config.py*.

Save with *Done* and hit the red *deploy* button on the upper right.

### 5. Have fun 😄 
The UI is now available on `http://localhost:1880/ui` and you should be able to control your LED strips from there 👍 


***


# Trouble?
open an issue on GitHub or write an email to 102shows@leiner.me
