from flask_migrate import upgrade
from sqlalchemy import func

from common import create_or_load_config, create_user, print_key
from forgesteel_warehouse import db, init_app
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

## Bootstrap the warehouse
if __name__ == "__main__":
    bootstrap()