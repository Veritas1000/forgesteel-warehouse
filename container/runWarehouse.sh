#!/bin/bash -e

python utils/bootstrap.py

gunicorn --config gunicorn_config.py 'forgesteel_warehouse:init_app()'
