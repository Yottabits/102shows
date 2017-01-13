==============
Using 102shows
==============

############
Installation
############

102shows consists of two parts:

- the **lightshow server**, which should run on a Raspberry Pi -
  it controls the LED strip via SPI - it listens for MQTT messages
  that tell it which show to start (and what the paramters for the
  show are)
- the **UI** - it delivers a nice web interface - it sends the MQTT
  messages to the server

For the two elements to be able to communicate (via MQTT) you need an
**MQTT broker**, for example ``mosquitto``

All of these can run on the same Raspberry Pi but only the server has
to.

MQTT broker
===========

If you already have an MQTT broker in your network, you can use it.
Else, install ``mosquitto`` via ``sudo apt-get install mosquitto``. In
any case, you will need the host, port (and maybe access credentials) of
your MQTT broker for later.

Server
======

In the folder you want to install 102shows in, run:

::

    wget -q -O 102s-setup.sh https://git.io/v1x1q; chmod +x 102s-setup.sh; ./102s-setup.sh; rm 102s-setup.sh

This will launch an assistant that will lead you through the
installation process.

Web UI
======

1. Prerequisites
----------------

The web UI depends on `Node-RED <https://nodered.org/>`__ with the
`dashboard <https://flows.nodered.org/node/node-red-dashboard>`__
add-on.

-  Install Node-RED: (this is **not necessary** on Raspbian)

   -  Install node.js (including npm): ``sudo apt-get install nodejs``
      (not necessary on Raspbian)
   -  Update npm: ``sudo npm install npm@latest -g``
   -  Install Node-RED: ``sudo npm install -g node-red``

-  Install the Node-RED dashboard add-on (**note that you have to
   uninstall any previous versions of node-red-contrib-ui etc. first**):
   ``npm install node-red-dashboard``

2. Start Node-RED
-----------------

Execute ``node-red`` on a console. The Node-RED administration interface
should now be available on ``http://localhost:1880``

.. topic:: Raspbian Tip

   If you want Node-RED to automatically start on boot, execute:
   ``sudo systemctl enable nodered.service``

3. Paste the 102shows UI in Node-RED
------------------------------------

Copy the contents of
`ui/nodered.json <https://raw.githubusercontent.com/Yottabits/102shows/stable/ui/nodered.json>`__
into the clipboard. Go to the Node-RED admin interface and in the main
menu (upper right corner) choose *Import* >> *Clipboard* and paste the
code you copied earlier into the window that is opening. Confirm with
*Import*

You should now see the flow **LED control**

4. Configure the 102shows UI
----------------------------

In the upper left of **LED control** there is a node named **global
settings**. Double-click on it to open it and modify the preferences in
the code so that they match the settings in your server-side
*config.py*.

Save with *Done* and hit the red *deploy* button on the upper right.

5. Have fun 😄
--------------

The UI is now available on ``http://localhost:1880/ui`` and you should
be able to control your LED strips from there 👍

#############
Configuration
#############

#FIXME

#######
Running
#######

Server
======

1. Start the MQTT broker
2. Execute ``/path/to/102shows/server/run.sh``

Web UI
======

Just start Node-RED. The panel shold appear on ``yournoderedhost:1880/ui``