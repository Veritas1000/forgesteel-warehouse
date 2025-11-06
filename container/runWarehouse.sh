#!/bin/bash -e

python bootstrap.py

gunicorn --config gunicorn_config.py 'forgesteel_warehouse:init_app()'
