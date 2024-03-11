from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

db = SQLAlchemy()

user_goal_association = db.Table(
    'user_goal_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('goal_id', db.Integer, db.ForeignKey('goal.id'))
)

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
    number_of_participants = db.Column(db.Integer, nullable=False) # This becomes number_of_participants
    user_id = db.Column(db.String(100), nullable=False) # This is the creator user_id
    participants = db.relationship('User', 
                                   secondary=user_goal_association, 
                                   back_populates='goals', 
                                   lazy='dynamic')

    def add_participant(self, user):
        """Add a participant to the goal."""
        if user not in self.participants:
            self.participants.append(user)
            self.number_of_participants += 1
            print(self.number_of_participants)

    def remove_participant(self, user):
        """Add a participant to the goal."""
        if user in self.participants:
            self.participants.remove(user)
            self.number_of_participants -= 1
            print(self.number_of_participants)

    

class User(db.Model, UserMixin):
    id = db.Column(db.String(6), primary_key=True) # This needs to be changed to a secret string
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    goals = db.relationship('Goal', secondary=user_goal_association, back_populates='participants', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    

