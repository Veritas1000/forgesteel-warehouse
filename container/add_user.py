from sqlalchemy import func
from forgesteel_warehouse.utils.app_utils import create_or_load_config, create_user, print_key
from forgesteel_warehouse import db, init_app
from forgesteel_warehouse.models import User

def add_user():
    config = create_or_load_config()
    app = init_app(config)
    with app.app_context():
        num_users = db.session.execute(func.count(User.id)).scalar()
        user_num = int(num_users) + 1 if num_users is not None else 42
        user_key = create_user(app, f"User {user_num}")
        print_key(user_key)

if __name__ == "__main__":
    add_user()
