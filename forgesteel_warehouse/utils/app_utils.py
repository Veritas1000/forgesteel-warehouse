import json
import os
import secrets
import textwrap
import uuid
from dotenv import load_dotenv
from flask_migrate import upgrade
from sqlalchemy import func

from forgesteel_warehouse import db, init_app
from forgesteel_warehouse.api_key import ApiKey
from forgesteel_warehouse.models import User

def add_default_user(app):
    return create_user(app, 'default_user')

def bootstrap():
    config = create_or_load_config()
    ## Initialize the DB
    app = init_app(config)
    with app.app_context():
        upgrade()
        ## Check if any user exists
        num_users = db.session.execute(func.count(User.id)).scalar()
        if num_users == 0:
            ## If the user does not exist, create the default user
            user_key = add_default_user(app)
            print_key(user_key)

def create_or_load_config():
    load_dotenv()
    config_path = os.getenv('FSW_CONFIG_PATH', '/data/config.json')
    with open(config_path, 'a+', encoding='utf-8') as config_file:
        config_file.seek(0)
        changed = False
        try:
            config = json.load(config_file)
        except Exception as e:
            config = {}

        if 'SECRET_KEY' not in config:
            config['SECRET_KEY'] = secrets.token_hex(64)
            changed = True
        if 'JWT_SECRET_KEY' not in config:
            config['JWT_SECRET_KEY'] = secrets.token_hex(64)
            changed = True

        if changed:
            config_file.seek(0)
            json.dump(config, config_file, ensure_ascii=False, indent=4)
            config_file.truncate()

    return config

def create_user(app, user_name):
    with app.app_context():
        key = uuid.uuid4().hex
        user = User(name=user_name, auth_key=key)
        db.session.add(user)
        db.session.commit()
        uid = user.id
        db.session.close()

        return ApiKey.makeApiKey(uid, key)

def print_key(key):
    banner = f"""
    {'*'*40}
    USER CREATED
    Here is your API KEY for connecting with Forge Steel
    Save it somewhere safe - IT WON'T BE DISPLAYED AGAIN!
    
    {key}

    {'*'*40}
    """
    print(textwrap.dedent(banner))
