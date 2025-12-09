#!/bin/bash -e

PROJ_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PYTHONPATH="${PYTHONPATH}:${PROJ_DIR}"

python container/utils/bootstrap.py

gunicorn --reload --config container/gunicorn_config.py 'forgesteel_warehouse:init_app()'
