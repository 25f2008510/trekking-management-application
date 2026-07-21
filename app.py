from flask import Flask
from flask_login import LoginManager
from models import db, User
from config import Config
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_admin():
    admin = User.query.filter_by(email='admin@trek.com').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@trek.com',
            password=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully')
    else:
        print('Admin already exists')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
        app.run(debug=True)