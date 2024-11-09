import os
from flask import Flask, redirect, render_template, request, session, url_for
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key needed to use Flask sessions

# Function for loading data based on category
def load_category(category):
    data_dict = {}
    file_path = os.path.join("data", f"{category}.txt")
    try:
        with open(file_path, mode='r') as file:
            for line in file:
                name, facts = line.strip().split(':')
                facts_list = [fact.strip() for fact in facts.split('/')]
                data_dict[name.strip()] = facts_list
    except FileNotFoundError:
        print(f"File for category '{category}' not found.")
    return data_dict

# Route for category selection
@app.route("/start_game")
def select_category():
    return render_template("category_selection.html")

@app.route("/start", methods=["POST"])
def start_game():
    category = request.form.get("category")
    data_dict = load_category(category)
    if not data_dict:
        return "No data found for the selected category.", 404

    random_key, random_value = random.choice(list(data_dict.items()))
    session["category"] = category
    session["country"] = random_key
    session["facts"] = random_value
    session['fact_index'] = 0
    session['total_points'] = 0
    session['tries'] = len(random_value)
    session['time_limit'] = 30

    current_fact = random_value[session['fact_index']]
    return render_template('index.html', fact=current_fact, tries=session['tries'])

# Route for guessing
@app.route('/guess', methods=['POST'])
def guess():
    country = session.get('country')
    facts = session.get('facts')
    fact_index = session.get('fact_index', 0)
    user_guess = request.form.get('guess', '').title()
    
    session['tries'] -= 1
    tries = session['tries']

    if user_guess == country:
        result = f"Correct! The answer was {country}."
        session['total_points'] += len(facts) - fact_index
        session.pop('country', None)
        return render_template('play.html', result=result, points=session['total_points'])
    else:
        fact_index += 1
        session['fact_index'] = fact_index

        if fact_index < len(facts):
            current_fact = facts[fact_index]
            return render_template('index.html', fact=current_fact, message="Wrong guess, try again!", tries=tries)
        else:
            result = f"Out of hints! The correct answer was {country}."
            session.pop('country', None)
            return render_template('play.html', result=result, points=session['total_points'])
@app.route('/')
def index():
    # Redirect to the start_game route when accessing the root URL
    return redirect(url_for('select_category'))

# Route for replaying the game
@app.route("/play_again")
def play_again():
    return redirect(url_for("select_category"))

if __name__ == '__main__':
    app.run(debug=True)
