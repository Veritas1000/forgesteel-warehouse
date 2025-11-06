import uuid
import textwrap

from sqlalchemy import func

from forgesteel_warehouse import db, init_app
from forgesteel_warehouse.models import User
from forgesteel_warehouse.api_key import ApiKey

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
    ## Initialize the DB
    app = init_app()
    with app.app_context():
        db.create_all()
        ## Check if any user exists
        default_user = db.session.execute(func.count(User.id)).scalar()
        if default_user == 0:
            ## If the user does not exist, create the default user
            user_key = add_default_user(app)
            print_key(user_key)
