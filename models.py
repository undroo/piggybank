from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

db = SQLAlchemy()

def init_db(app):
    # Set the SQLite database file path
    db_path = os.path.join(app.root_path, 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

    # Suppress a warning about track_modifications, which is unnecessary for SQLite
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'iamapotato' # change this to use a secret file with a secret key
    db.init_app(app)
    # Check if the database file exists, and create it if not
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()

# This model needs to expand, participants will eventually be a list of people
class Goal(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    savings_goal = db.Column(db.Float, nullable=False)
    participants = db.Column(db.Integer, nullable=False) # This becomes number_of_participants
    user_id = db.Column(db.String(100), nullable=False)

class User(db.Model, UserMixin):
    # id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    

