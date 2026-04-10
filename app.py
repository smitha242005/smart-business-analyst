from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
from agents.cleaning_agent import clean_data
from agents.prediction_agent import predict_sales
from agents.recommendation_agent import get_recommendations
from database import init_db, get_user_by_email, create_user, get_user_by_id, save_analysis, get_user_history
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.secret_key = 'smartbusiness2025secretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
init_db()

# ===== Auth Routes =====

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        success = create_user(username, email, hashed_password)

        if success:
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email or username already exists!', 'danger')
            return render_template('register.html')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_user_by_email(email)

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash(f'Welcome back, {user[1]}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password!', 'danger')
            return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ===== Main Routes =====

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'))

@app.route('/upload')
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('upload.html', username=session.get('username'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_history = get_user_history(session['user_id'])
    history_list = []
    for record in user_history:
        history_list.append({
            'id': record[0],
            'filename': record[2],
            'predicted_sales': record[3],
            'predicted_profit': record[4],
            'accuracy': record[5],
            'recommendations': json.loads(record[6]) if record[6] else [],
            'created_at': record[7]
        })
    return render_template('history.html', 
                         username=session.get('username'),
                         history=history_list)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    df = clean_data(filepath)
    results = predict_sales(df)
    recommendations = get_recommendations(results)

    # Save to history
    save_analysis(
        user_id=session['user_id'],
        filename=file.filename,
        predicted_sales=results['predicted_sales'],
        predicted_profit=results['predicted_profit'],
        accuracy=results['accuracy'],
        recommendations=recommendations
    )

    return jsonify({
        'predicted_sales': results['predicted_sales'],
        'predicted_profit': results['predicted_profit'],
        'accuracy': results['accuracy'],
        'mae': results['mae'],
        'rmse': results['rmse'],
        'chart_data': results['chart_data'],
        'recommendations': recommendations
    })

if __name__ == '__main__':
    app.run(debug=True)