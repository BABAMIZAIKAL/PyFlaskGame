import uuid
import os

from flask import Flask
from flask import render_template, request, redirect, make_response, url_for, flash

from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
from flask_socketio import SocketIO, join_room, send, emit
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from database import db_session, init_db
from sqlalchemy import text
from login import login_manager
from models import User, Lobby


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "ssucuuh398nuwetubr33rcuhne"
login_manager.init_app(app)
init_db()
socketio = SocketIO(app)
migrate = Migrate(app, SQLAlchemy(app))

salt = "plough"

@app.teardown_appcontext
def shutdown_context(exception=None):
    db_session.remove()

@app.route('/profile', methods=['GET', 'POST'])
def profile():
	if request.method == 'GET':
		return render_template('profile.html', user=current_user)
	
		
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', user=current_user, lobbies = Lobby.query.all())
    else:
        print(request.data)
        return redirect(url_for("create_lobby"))
        
        
@app.route('/create_lobby', methods=['GET', 'POST'])
def create_lobby():
    if current_user.is_authenticated:
        if request.method == 'GET':
            lobby = Lobby(user1=current_user.id, gameState="         ")
            print(current_user.get_id())
            db_session.add(lobby)
            db_session.commit()
            print({'id' : lobby.id})
            return {'id' : lobby.id}
    else:
        return {'id' : -1}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            return redirect(url_for('register'))
        password = generate_password_hash(request.form['password'] + salt)

        user = User(username=username, password=password)
        db_session.add(user)
        db_session.commit()
        user.login_id = str(uuid.uuid4())
        db_session.commit()
        login_user(user)
        return redirect(url_for('index'))
        

@app.route('/login', methods=['GET', 'POST'])
def login():
    #response = None
    if request.method == 'GET':
        return render_template('login.html')
    else:	
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
        	user.login_id = str(uuid.uuid4())
        	db_session.commit()
        	login_user(user)
    return redirect(url_for('index'))
       
@app.route("/logout")
@login_required
def logout():
    current_user.login_id = None
    db_session.commit()
    logout_user()
    return redirect(url_for('login'))

@app.route('/lobby/<int:lobby_id>', methods=['GET', 'POST'])
def lobby(lobby_id):
    curr_lobby = Lobby.query.filter_by(id=lobby_id).first()
    code = generate_password_hash(str(lobby_id) + salt)
    print(code)
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if not curr_lobby.user2 == None and current_user.id != curr_lobby.user1 and current_user.id != curr_lobby.user2:
        return redirect(url_for('index'))
    if curr_lobby.user2 == None and current_user.id != curr_lobby.user1:
        db_session.execute(text("update lobby set user2 = " + str(current_user.id) + " where id = "+ str(curr_lobby.id) + ";"))
        db_session.commit()
        pass
    #if not Lobby.query.filter_by(id=lobby_id).first():
    #    newLobby = Lobby(id=lobby_id, user1 = current_user.id, gameState="ttttttttt")
    #    db_session.add(newLobby)
    #    db_session.commit()
    #    print(Lobby.query.all())
    if curr_lobby.user2 == None:
        flash("Lobby code: " + str(hex(curr_lobby.id * 429606841))[2:])
    return render_template("lobby.html", lobby_id = lobby_id, user1 = User.query.filter_by(id=curr_lobby.user1).first(), user2 = User.query.filter_by(id=curr_lobby.user2).first())

@app.route('/code', methods=['GET', 'POST'])
def code():    
    if request.method == 'GET':
        return render_template("code.html")
    else:
        code = request.form['code']
        for lobby in Lobby.query.all():
            print(code)
            print(hex(lobby.id * 429606841))
            if str(hex(lobby.id * 429606841))[2:] == code:
                return redirect(url_for('lobby', lobby_id=lobby.id))
        flash("Invalid code", 'warning')
        return redirect(url_for('code'))
        
@socketio.on('join')
def on_join(data):
    room_id = data['room']
    print("Room id is {}".format(room_id))
    join_room(room_id)
    curr_lobby = Lobby.query.filter_by(id=data['room']).first()
    if curr_lobby.user2 != None and data['sender'] != curr_lobby.user1:
        print(data)
        emit("refresh",{'sender':data['sender']},room=room_id)
        


@socketio.on('move')
def on_move(data):
    room_id = data['room']
    curr_lobby = Lobby.query.filter_by(id=data['room']).first()
    curr_lobby.gameState = curr_lobby.gameState[:int(data['move'])] + ["O","X"][data['x']==data['sender']] + curr_lobby.gameState[int(data['move'])+1:]
    db_session.commit()
    emit("move", {'gameState' : curr_lobby.gameState}, room = room_id)

@socketio.on('disconnect')
def on_disconnect(data):
    room_id = data['room']
    leave_room(room_id)
    emit('leaving', data, room=room_id)
    pass

if __name__ == '__main__':
    socketio.run(app)
