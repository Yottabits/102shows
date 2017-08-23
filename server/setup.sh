#!/bin/bash

RED='\033[0;31m'
LIGHTRED='\033[1;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
LIGHTBLUE='\033[1;34m'
LIGHTCYAN='\033[1;36m'
NOCOLOR='\033[0m' # No Color

GLOBAL_PYTHON3='/usr/bin/python3'
BRANCH='stable'

function check_tty() {
    if ! [[ -t 1 ]]; then
        msg_error " => You need an interactive terminal to run this script!"
        exit
    fi
}

function parse_branch() {
    local number_of_arguments=${#BASH_ARGV[@]}

    if [[ number_of_arguments -eq 0 ]]; then
        msg_success "=> No branch supplied as argument. Using ${BRANCH}"
    else
        BRANCH=${BASH_ARGV[0]}
        msg_success "=> Using repository branch ${BRANCH}."
    fi
}

function status_update() {
    echo -e "\n${LIGHTBLUE}$@${NOCOLOR}"
}

function msg_error() {
    echo -e "\n${LIGHTRED}$@${NOCOLOR}"
}

function msg_success() {
    echo -e "\n${GREEN}$@${NOCOLOR}"
}

function question() {
    echo -en "${LIGHTCYAN}$@${NOCOLOR}"
}

function install_dependencies()
{
    status_update " => Installing required software"
    sudo apt-get install python3 python3-venv python3-pip
}

function install()
{
    install_dependencies
    
    status_update " => Getting the latest ${BRANCH} release from GitHub"
    git clone -b ${BRANCH} https://github.com/Yottabits/102shows.git
    rc=$?; if [[ ${rc} == 0 ]]; then   # check for success
        msg_success " => Download finished!"
    else
        msg_error " => Download failed! (return code: $rc)"
        msg_error "    Exiting installation!"
        exit ${rc}
    fi


    cd 102shows
    rm ./server/setup.sh  # remove this installer
    chmod u+x ./server/run.sh  # make runner executable

    status_update " => Setting up a Python3 virtual environment"
    eval ${GLOBAL_PYTHON3} -m venv venv
    rc=$?; if [[ ${rc} == 0 ]]; then   # check for success
        msg_success " => venv successfully created!"
    else
        msg_error " => venv creation failed!"
        msg_error "    Try 'sudo apt-get install python3-venv'"
        exit ${rc}
    fi
    source venv/bin/activate  # set the new interpreter as the default for python3, pip, setuptools,...


    status_update " => Installing required Python libraries"
    pip3 install -r ./requirements.txt
    rc=$?; if [[ ${rc} == 0 ]]; then   # check for success
        msg_success " => Requirements are ready!"
    else
        msg_error " => Installation of required Python libraries failed! (return code: $rc)"
        msg_error "    Maybe You do not have sufficient rights - try running this script with sudo..."
        msg_error "    For now I am going to quit the installation."
        exit ${rc}
    fi

    status_update " => Installing an executable under /bin/102shows-server"
    sudo rm /bin/102shows-server
    echo "#!/bin/bash

$PWD/server/run.sh""" | sudo tee -a /bin/102shows-server > /dev/null

    sudo chmod +x /bin/102shows-server

    status_update " => Installing a systemd service"
    sudo rm /etc/systemd/system/102shows-server.service
    sudo mv ./server/102shows-server.service /etc/systemd/system/102shows-server.service
    
    question " => Would you like to enable the service now? [Y/n]  "
    read answer < /dev/tty
    if [ "$answer" != "n" ] && [ "$answer" != "N" ]; then
        sudo systemctl enable 102shows-server
        msg_success " => To start the service now, execute: \"sudo service 102shows-server start\""
    else
        status_update " => If you want enable it later, execute: \"sudo systemctl enable 102shows-server\""
    fi

    echo -e  "$(cat logo)  version: $(cat version)"
    echo -e "\n\n"


    question " => Would you like to configure 102shows now? [Y/n]  "
    read answer < /dev/tty
    if [ "$answer" != "n" ] && [ "$answer" != "N" ]; then
        status_update " => copying config.example.yml to config.yml"
        cp ./server/config.example.yml ./server/config.yml
        status_update " => starting editor"
        editor ./server/config.yml < /dev/tty
        status_update " => editor stopped"
    else
        msg_error " => Before you can start the 102shows server,"
        msg_error "    you must provide a valid configuration file"
        msg_error "    in \"102shows/server/config.yml\""
    fi

    msg_success "
 => We successfully installed the 102shows server :-)
      - Note that you need an MQTT broker in order for the server to work
      - If you want to use the included UI, you should install it now
        You can find the instructions at https://goo.gl/lvGYzV
      - To run the server, start the MQTT broker and then execute $PWD/server/run.sh"
}

function main()
{
    check_tty
    question " => Would you like to install 102shows to $PWD/102shows? [y/N]  "
    read answer < /dev/tty
    if [ "$answer" == "y" ] || [ "$answer" == "Y" ]
    then
        parse_branch
        install
    fi

}

main
