import sys
import uuid

from common import create_or_load_config, print_key
from forgesteel_warehouse import db, init_app
from forgesteel_warehouse.api_key import ApiKey
from forgesteel_warehouse.models import User

def cycle_key(uid):
    config = create_or_load_config()
    app = init_app(config)
    with app.app_context():
        user = db.session.execute(db.select(User).filter_by(id=uid)).scalar_one_or_none()

        if user is not None:
            new_key = uuid.uuid4().hex
            user.set_auth_key(new_key)
            db.session.commit()
            api_key = ApiKey.makeApiKey(uid, new_key)
            print_key(api_key)

if __name__ == "__main__":
    user_id = 1
    if len(sys.argv) > 1 and int(sys.argv[1]) is not None:
        user_id = sys.argv[1]

    cycle_key(user_id)
