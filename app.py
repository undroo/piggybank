from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# List to store user inputs
savings_goals = []

# Counter for generating unique IDs
goal_id_counter = 1

@app.route('/')
def index():
    global goal_id_counter  # Declare goal_id_counter as a global variable
    return render_template('index.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    global goal_id_counter  # Declare goal_id_counter as a global variable
    name = request.form.get('name')
    savings_goal = float(request.form.get('savings_goal'))
    participants = float(request.form.get('participants'))

    
    # Generate a unique ID for the savings goal
    goal_id = goal_id_counter
    goal_id_counter += 1

    # Add the savings goal with ID and participant count to the list
    savings_goals.append({'id': goal_id, 'name': name, 'goal': savings_goal, 'participants': participants})


    # Redirect to the route displaying the details of the latest goal
    return redirect(url_for('view_goal', goal_id=goal_id))

@app.route('/view_goal', methods=['GET', 'POST'])
def search_goal():
    if request.method == 'POST':
        # If the form is submitted, get the goal_id from the form
        goal_id = request.form.get('goal_id')
        
        # Redirect to the view_goal route with the specified goal_id
        return redirect(url_for('view_goal', goal_id=goal_id))

    # If it's a GET request, render the search_goal.html template
    return render_template('search_goal.html')

@app.route('/view_goal/<int:goal_id>')
def view_goal(goal_id):
    # Find the goal with the specified ID
    goal = next((goal for goal in savings_goals if goal['id'] == goal_id), None)

    # If goal is not found, render a template with a message
    if goal is None:
        return render_template('no_goals.html')

    # Render the template with the specific goal
    return render_template('view_goal.html', goal=goal)

if __name__ == '__main__':
    app.run(debug=True)
