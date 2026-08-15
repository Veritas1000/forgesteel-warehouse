#!/bin/bash -e

PROJ_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PYTHONPATH="${PYTHONPATH}:${PROJ_DIR}"

echo "===  Starting warehouse dev server  ==="
echo "Using directory: $PROJ_DIR"

## Do a simple check to see if there is a config dir set via env var or .env file
echo "Checking for config path to be set"
if [ -z "$FSW_CONFIG_PATH" ]
then
    echo "Not set as an env var. Checking for .env"
    if ! `grep 'FSW_CONFIG_PATH' "${PROJ_DIR}/.env" > /dev/null 2>&1`
    then
        echo "Not found in .env"
        echo "Creating a basic .env with a default config"
        echo "FSW_CONFIG_PATH=./instance/config.json" > "${PROJ_DIR}/.env"
    else
        echo ".env file detected"
    fi
else
    echo "FSW_CONFIG_PATH=${FSW_CONFIG_PATH}"
fi

python container/standalone.py
