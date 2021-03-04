import uuid
import os

from flask import Flask
from flask import render_template, request, redirect, make_response, url_for

from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date

from database import db_session, init_db
from login import login_manager
from models import User, Lobby


app = Flask(__name__)
app.secret_key = "ssucuuh398nuwetubr33rcuhne"
login_manager.init_app(app)
init_db()


@app.teardown_appcontext
def shutdown_context(exception=None):
    db_session.remove()

@app.route('/profile', methods=['GET', 'POST'])
def profile():
	if request.method == 'GET':
		return render_template('profile.html', user=current_user)
	
		
@app.route('/', methods=['GET', 'POST'])
def homepage():
	if request.method == 'GET':
		return render_template('homepage.html', user=current_user, lobbies = Lobby.query.all())
		
@app.route('/create_lobby', methods=['GET', 'POST'])
@login_required
def create_lobby():
	if request.method == 'POST':
		
		user = request.form['user']

		lobby = Lobby(user1=user)
		db_session.add(lobby)
		db_session.commit()
		return redirect(url_for('profile'))
		
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        user = User(username=username, password=password)
        db_session.add(user)
        db_session.commit()
        return redirect(url_for('login'))
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    response = None
    if request.method == 'GET':
        return render_template('login.html')
    else:	
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
        	user.login_id = str(uuid.uuid4())
        	db_session.commit()
        	login_user(user)
    return redirect(url_for('homepage'))
       
@app.route("/logout")
@login_required
def logout():
    current_user.login_id = None
    db_session.commit()
    logout_user()
    return redirect(url_for('login'))
