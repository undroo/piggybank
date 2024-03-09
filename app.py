from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session
import string
import secrets
import os
from flask_wtf.csrf import CSRFProtect
# Internal libraries
from models import db, User, init_db, Goal
from forms import RegisterForm, LoginForm, GoalForm, SearchGoalForm

app = Flask(__name__)
init_db(app)
csrf = CSRFProtect(app)
# Initialize the database



# Move this to a helper.py
def generate_goal_id():
    # Generate a random 6-character string of numbers and letters
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))



@app.context_processor
def inject_search_goal_form():
    search_goal_form = SearchGoalForm()
    return dict(search_goal_form=search_goal_form)


# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            # Log in the user (you might use Flask-Login for this)
            session['user_id'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Check your username and password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # If the form is valid, create a new user and add them to the database
        # You can access form data using form.username.data, form.email.data, etc.

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            # password=User.set_password(form.password.data)
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    # Log out the user
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    form = GoalForm()
    # global goal_id_counter  # Declare goal_id_counter as a global variable
    if request.method == 'POST':
        # If the form is submitted, get the goal_id from the form
        goal_id = request.form.get('goal_id')
        
        # Redirect to the view_goal route with the specified goal_id
        return redirect(url_for('view_goal', goal_id=goal_id))
    return render_template('index.html', form=form)

@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))

    # Get the user's goals (customize this based on your database structure)
    user_id = session['user_id']
    # This doesn't work yet
    # user_goals = Goal.query.filter_by(user_id=user_id).all()
    all_goals = Goal.query.all()

    return render_template('dashboard.html', user_goals=all_goals)

@app.route('/process_form', methods=['POST'])
def process_form():
    if 'user_id' not in session:
        flash('You need to log in to add a goal.', 'warning')
        return redirect(url_for('login'))

    form = GoalForm(request.form)

    if form.validate_on_submit():
        user_id = session['user_id']
        # Generate a unique ID for the savings goal
        goal_id = generate_goal_id()

        new_goal = Goal(
            id=goal_id,
            name=form.name.data,
            savings_goal=form.savings_goal.data,
            participants=form.participants.data,
            user_id=user_id
        )

        db.session.add(new_goal)
        db.session.commit()

        flash('Goal added successfully!', 'success')
    else:
        flash('Error in adding the goal. Please check the form.', 'danger')

    # Redirect to the route displaying the details of the latest goal
    return redirect(url_for('view_goal', goal_id=goal_id))

@app.route('/search_goal', methods=['GET', 'POST'])
def search_goal():
    if request.method == 'POST':
        form = SearchGoalForm(request.form)
        # If the form is submitted, get the goal_id from the form
        goal_id = form.goal_id.data
        
        # Redirect to the view_goal route with the specified goal_id
        return redirect(url_for('view_goal', goal_id=goal_id))
    
    # We shouldn't need this anymore, potentially move to only be a POST?
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

    # TODO: add more features to this view_goal page
    # ability to 'complete' goals 
    # ability to delete goals
    # TODO: when bank is ready, need the ability to check for payments made to this

    # Render the template with the specific goal
    return render_template('view_goal.html', goal=goal)

if __name__ == '__main__':
    app.run(debug=True)
