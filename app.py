from flask import Flask, render_template, request, redirect, url_for
import string
import secrets
import os

app = Flask(__name__)

# List to store user inputs
savings_goals = []

def generate_goal_id():
    # Generate a random 6-character string of numbers and letters
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))

from flask_sqlalchemy import SQLAlchemy

# Set the SQLite database file path
db_path = os.path.join(app.root_path, 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

# Suppress a warning about track_modifications, which is unnecessary for SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Goal(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    savings_goal = db.Column(db.Float, nullable=False)
    participants = db.Column(db.Integer, nullable=False)

# Check if the database file exists, and create it if not
if not os.path.exists(db_path):
    with app.app_context():
        db.create_all()


    


@app.route('/', methods=['GET', 'POST'])
def index():
    # global goal_id_counter  # Declare goal_id_counter as a global variable
    if request.method == 'POST':
        # If the form is submitted, get the goal_id from the form
        goal_id = request.form.get('goal_id')
        
        # Redirect to the view_goal route with the specified goal_id
        return redirect(url_for('view_goal', goal_id=goal_id))
    return render_template('index.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    global goal_id_counter  # Declare goal_id_counter as a global variable
    name = request.form.get('name')
    savings_goal = float(request.form.get('savings_goal'))
    participants = float(request.form.get('participants'))

    

    # Generate a unique ID for the savings goal
    goal_id = generate_goal_id()

    # TODO: change this to use a database
    # Add the savings goal with ID and participant count to the list
    new_goal = Goal(id=goal_id,name=name, participants=participants, savings_goal=savings_goal)
    db.session.add(new_goal)
    db.session.commit()

    savings_goals.append({
        'id': goal_id, 
        'name': name, 
        'goal': savings_goal, 
        'participants': participants})


    # Redirect to the route displaying the details of the latest goal
    return redirect(url_for('view_goal', goal_id=goal_id))

@app.route('/search_goal', methods=['GET', 'POST'])
def search_goal():
    if request.method == 'POST':
        # If the form is submitted, get the goal_id from the form
        goal_id = request.form.get('goal_id')
        
        # Redirect to the view_goal route with the specified goal_id
        return redirect(url_for('view_goal', goal_id=goal_id))
    # If it's a GET request, render the search_goal.html template
    goal_id = request.args.get('goal_id')
    if goal_id is not None:
        return redirect(url_for('view_goal', goal_id=goal_id))
    return render_template('search_goal.html')

@app.route('/view_goal/<string:goal_id>')
def view_goal(goal_id):
    # Find the goal with the specified ID
    # goal = next((goal for goal in savings_goals if goal['id'] == goal_id), None)
    goal = Goal.query.filter_by(id=goal_id).first()

    # If goal is not found, render a template with a message
    if goal is None:
        return render_template('no_goals.html')

    # Render the template with the specific goal
    return render_template('view_goal.html', goal=goal)

if __name__ == '__main__':
    app.run(debug=True)
