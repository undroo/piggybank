from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session
import string
import secrets
import os
from flask_wtf.csrf import CSRFProtect
# Internal libraries
from models import db, User, init_db, Goal, user_goal_association
from forms import RegisterForm, LoginForm, GoalForm, SearchGoalForm, DeleteGoalForm, JoinGoalForm

app = Flask(__name__)
init_db(app)
csrf = CSRFProtect(app)
# Initialize the database



# Move this to a helper.py
def generate_goal_id():
    # Generate a random 6-character string of numbers and letters
    while True:
        # Generate a random 6-digit ID
        goal_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))

        # Check if the ID is already in use
        if not Goal.query.filter_by(id=goal_id).first():
            return goal_id

def generate_user_id():
    while True:
        # Generate a random 6-digit ID
        user_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))

        # Check if the ID is already in use
        if not User.query.filter_by(id=user_id).first():
            return user_id

def is_creator(user_id, goal):
    """Check if the user is the creator of the goal."""
    return str(goal.user_id) == str(user_id)

def is_participant(user_id, goal_id):
    """Check if the user is a participant in the goal."""

    return db.session.query(user_goal_association).filter_by(user_id=user_id, goal_id=goal_id).count() > 0
    # return user in goal.participants


# Function for the navbar
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
            session['user_id'] = user.id
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
            id = generate_user_id(),
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
    return redirect(url_for('login'))

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
    
    user = db.session.get(User, user_id)
    user_goals = user.goals.all()

    return render_template('dashboard.html', user_goals=user_goals)

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
            number_of_participants=form.participants.data,
            user_id=user_id
        )
        # Get the current user and append the new goal
        user = db.session.get(User,user_id)
        new_goal.participants.append(user) # Add user to list of participants
        user.goals.append(new_goal) # Add goal to list of goals for user


        # Commit both changes in a single database transaction
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
    goal = db.session.get(Goal, goal_id)

    # If goal is not found, render a template with a message
    if goal is None:
        return render_template('no_goals.html')

    # TODO: add more features to this view_goal page
    # ability to 'complete' goals 
    # ability to delete goals
    # ability to join goals
    # TODO: when bank is ready, need the ability to check for payments made to this

    if 'user_id' in session:
        user_id = session['user_id']
        # user = db.session.get(User, user_id)

        # Check if the user is the creator of the goal
        is_creator_goal = is_creator(user_id, goal)
        # Check if the user is a participant in the goal, creators are already participating
        is_participant_goal = is_participant(user_id, goal_id)
        # is_participant_goal == True if is_creator_goal else is_participant_goal

        return render_template('view_goal.html', 
                               goal=goal, is_creator_goal=is_creator_goal, 
                               is_participant=is_participant_goal)
    

    # Render the template with the specific goal
    return render_template('view_goal.html', 
                           goal=goal, 
                           is_creator_goal=False,
                           is_participant=False)

@app.route('/delete_goal/<string:goal_id>', methods=['POST'])
def delete_goal(goal_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in to delete a goal.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    goal = db.session.get(Goal, goal_id)

    # Check if the user is the creator of the goal
    if goal and str(goal.user_id) == str(user_id):
        try:
            # Delete the goal and commit changes
            db.session.refresh(goal)
            db.session.delete(goal)
            db.session.commit()
            flash('Goal deleted successfully!', 'success')
        except Exception as e:
            print(e)
            db.session.rollback()
            # Retry the operation or handle it appropriately
    else:
        flash('You do not have permission to delete this goal.', 'danger')

    return redirect(url_for('dashboard'))

@app.route('/join_goal/<string:goal_id>', methods=['POST'])
def join_goal(goal_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in to join a goal.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = db.session.get(User,user_id)
    goal = db.session.get(Goal,goal_id)
    
    # Check if the user is not already a participant in the goal
    if goal and user and user not in goal.participants:
        # Add the user to the goal's participants
        goal.add_participant(user)

        # Add the goal to the user's list of goals
        user.goals.append(goal)

        # db.session.refresh(goal)
        db.session.commit()

        flash('You have successfully joined the goal!', 'success')
        return redirect(url_for('view_goal', goal_id=goal_id))
    else:
        flash('You are already a participant in this goal.', 'danger')
        return redirect(url_for('view_goal', goal_id=goal_id))

@app.route('/leave_goal/<string:goal_id>', methods=['POST'])
def leave_goal(goal_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in to leave a goal.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    goal = db.session.get(Goal,goal_id)

    # Check if the user is a participant in the goal
    is_participant_goal = is_participant(user_id, goal_id)

    # Check if the user is the creator of the goal
    is_creator_goal = (goal.user_id == user_id if goal else False)

    if is_participant_goal and not is_creator_goal:
        # Remove the user from the goal's participants
        user = db.session.get(User,user_id)
        goal.remove_participant(user)

        # Remove the goal from the user's list of goals
        user.goals.remove(goal)

        db.session.commit()

        flash('You have successfully left the goal.', 'success')
    else:
        flash('You cannot leave the goal. Either you are not a participant or you are the creator.', 'danger')

    return redirect(url_for('view_goal', goal_id=goal_id))

if __name__ == '__main__':
    app.run(debug=True)
