#!/bin/bash

# the server dir is the directory this script is located in
# so lets get the server directory
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  SERVER_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
  [[ ${SOURCE} != /* ]] && SOURCE="$SERVER_DIR/$SOURCE"
done
SERVER_DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd ${SERVER_DIR}

source ../venv/bin/activate
python3 server.py
