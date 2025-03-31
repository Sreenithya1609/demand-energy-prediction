from flask import Flask, render_template, request, redirect, url_for, flash, session
import pickle
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this for production

# Sample user database (replace with real database in production)
users = {
    "admin": generate_password_hash("admin123"),
    "user": generate_password_hash("user123")
}

# Load ML model
try:
    model = pickle.load(open('random_forest_model.pkl', 'rb'))
except:
    model = None
    print("Model not loaded - prediction functionality disabled")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            flash('Login successful!', 'success')
            next_page = request.args.get('next') or url_for('prediction_form')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')
# Add this new route to your existing app.py
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation checks
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        
        if username in users:
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))
        
        # Add new user
        users[username] = generate_password_hash(password)
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/PredictionForm')
def prediction_form():
    if 'username' not in session:
        flash('Please login to access the prediction form', 'warning')
        return redirect(url_for('login', next=request.endpoint))
    return render_template('prediction_form.html')

@app.route('/result', methods=['POST'])
def result():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get form data
        features = [
            float(request.form['state_code']),
            float(request.form['state_name']),
            float(request.form['region']),
            float(request.form['wind_energy']),
            float(request.form['solar_energy']),
            float(request.form['other_renewable'])
        ]
        
        # Make prediction
        if model:
            prediction = model.predict([features])[0]
        else:
            prediction = "Model not available"
            flash('Prediction model not loaded', 'error')
        
        return render_template('result.html', prediction=prediction)
    
    except Exception as e:
        flash(f'Error in prediction: {str(e)}', 'error')
        return redirect(url_for('prediction_form'))

if __name__ == '__main__':
    app.run(debug=True)