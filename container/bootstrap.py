import uuid
import textwrap
import json
import os

from sqlalchemy import func

from forgesteel_warehouse import db, init_app
from forgesteel_warehouse.models import User
from forgesteel_warehouse.api_key import ApiKey

def create_or_load_config():
    config_path = os.getenv('FSW_CONFIG_PATH', '/data/config.json')
    with open(config_path, 'w+', encoding='utf-8') as config_file:
        changed = False
        try:
            config = json.load(config_file)
        except:
            config = {}

        if 'SECRET_KEY' not in config.keys():
            config['SECRET_KEY'] = uuid.uuid4().hex
            changed = True
        if 'JWT_SECRET_KEY' not in config.keys():
            config['JWT_SECRET_KEY'] = uuid.uuid4().hex
            changed = True

        if changed:
            json.dump(config, config_file, ensure_ascii=False, indent=4)

    return config

def add_default_user(app):
    with app.app_context():
        db.create_all()
        key = uuid.uuid4().hex
        user = User(name='default_user', auth_key=key)
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

## Bootstrap the warehouse
if __name__ == "__main__":
    config = create_or_load_config()
    ## Initialize the DB
    app = init_app(config)
    with app.app_context():
        db.create_all()
        ## Check if any user exists
        default_user = db.session.execute(func.count(User.id)).scalar()
        if default_user == 0:
            ## If the user does not exist, create the default user
            user_key = add_default_user(app)
            print_key(user_key)
