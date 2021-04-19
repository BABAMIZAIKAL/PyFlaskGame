import uuid
import os

from flask import Flask
from flask import render_template, request, redirect, make_response, url_for, flash

from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
from flask_socketio import SocketIO, join_room, send, emit, leave_room
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from database import db_session, init_db
from sqlalchemy import text
from login import login_manager
from models import User, Lobby, TicTacToeLobby, HangmanLobby
#from models import User, Lobby

games_all = ["TicTacToe", "Hangman"]

def generateLobbyCode(a):
	return str(hex(a * 429606841)[2:])

def codeToInt(a):
	print(a)
	return int('0x' + a, 16) / 429606841

#SQL queries
def handleQueryLobbyType(lobbyType, id):
	print(id)
	print(str(id))
	curr_lobby = db_session.execute(text("select * from " + lobbyType + "lobby" + " where id = " + str(id) + " limit 1;")).first();
	return curr_lobby

def handleCreateLobbyType(lobbyType, data):
	lobby = None
	if lobbyType == "tictactoe":
		lobby = TicTacToeLobby(user1 = data[0], gameState = data[2])
	elif lobbyType == "hangman":
		lobby = HangmanLobby(user1 = data[0], gameState = data[2])
	#lobby = db_session.execute("insert into " + lobbyType + "lobby(user1, user2, gameState)" + " values(" + ", ".join(str(a) for a in data) + ") returning *;"))
	db_session.add(lobby)
	db_session.commit()
	return lobby.id

def handleStateUpdate(lobbyType, id, newState):
	db_session.execute(text("update " + lobbyType + "lobby" + " set gameState = \"" + newState + "\" where id = "+ str(id) + ";"))
	db_session.commit()

def handleLobbyUpdate(lobbyType, id, id2):
	print(id2)
	db_session.execute(text("update " + lobbyType + "lobby" + " set user2 = " + str(id2) + " where id = "+ str(id) + ";"))
	db_session.commit()

def handleQueryUser(id):
	return db_session.execute(text("select * from users where id = " + str(id) + ";")).first()

#actual app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "ssucuuh398nuwetu"
login_manager.init_app(app)
init_db()
socketio = SocketIO(app)
migrate = Migrate(app, SQLAlchemy(app))

salt = "PZ1Rtqrul5kECoKh"


@app.teardown_appcontext
def shutdown_context(exception=None):
	db_session.remove()

@app.route('/profile', methods=['GET', 'POST'])
def profile():
	if request.method == 'GET':
		return render_template('profile.html', user=current_user, directory = "../")

@app.route('/scoreboard', methods=['GET', 'POST'])
def scoreboard():
	if request.method == 'GET':
		return render_template('scoreboard.html', users=User.query.order_by(desc(User.score_tictactoe)), directory = "../")
	
		
@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html', user=current_user, game_types = games_all, directory = "../")
	else:

		print(request.form)
		return redirect(url_for("create_lobby", lobby_type = request.form['lobby type']))
		
		
@app.route('/create_lobby/<lobby_type>', methods=['GET', 'POST'])
def create_lobby(lobby_type):
	if current_user.is_authenticated:
		if request.method == 'GET':
			placeholder = current_user.get_id_2()
			id = handleCreateLobbyType(lobby_type, [placeholder, 'null', "         "])
			return {'lobby_type' : lobby_type, 'lobby_id' : id}
			return redirect(url_for("lobby", lobby_type = lobby_type, lobby_id = id))
	else:
		return {'id' : -1}

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html', directory = "../")
	else:
		print(request.form)
		username = request.form['username']
		if User.query.filter_by(username=username).first():
			print(User.query.filter_by(username=username).first())
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
		return render_template('login.html', directory = "../")
	else:	
		user = User.query.filter_by(username=request.form['username']).first()
		if user and check_password_hash(user.password, request.form['password'] + salt):
			user.login_id = str(uuid.uuid4())
			db_session.commit()
			login_user(user)
			return redirect(url_for('index'))
		return render_template("login.html", directory = "../")

@app.route("/logout")
@login_required
def logout():
	current_user.login_id = None
	db_session.commit()
	logout_user()
	return redirect(url_for('login'))

@app.route('/lobby/<lobby_type>/<int:lobby_id>', methods=['GET', 'POST'])
def lobby(lobby_id, lobby_type):
	curr_lobby = handleQueryLobbyType(lobby_type, lobby_id)
	#code = generate_password_hash(str(lobby_id) + salt)
	#print(code)
	if not current_user.is_authenticated:
		return redirect(url_for('login'))
	if curr_lobby.user2 != None and current_user.id != curr_lobby.user1 and current_user.id != curr_lobby.user2:
		return redirect(url_for('index'))
	#if not Lobby.query.filter_by(id=lobby_id).first():
	#	newLobby = Lobby(id=lobby_id, user1 = current_user.id, gameState="ttttttttt")
	#	db_session.add(newLobby)
	#	db_session.commit()
	#	print(Lobby.query.all())
	if curr_lobby.user2 == None:
		flash("Lobby code: " + generateLobbyCode(curr_lobby.id))
	return render_template("lobby/" + lobby_type + ".html", lobby_id = lobby_id, user1 = User.query.filter_by(id=curr_lobby.user1).first(), user2 = User.query.filter_by(id=curr_lobby.user2).first(), directory = "../../")

@app.route('/code/<lobby_type>', methods=['GET', 'POST'])
def code(lobby_type):	
	if request.method == 'GET':
		return render_template("code.html", lobby_type = lobby_type, directory = "../")
	else:
		code = request.form['code']
		print(code)
		lobby = handleQueryLobbyType(lobby_type, codeToInt(code))
		print(lobby)
		if lobby:
			print(url_for('lobby', lobby_type = lobby_type.lower(), lobby_id=lobby.id))
			return redirect(url_for('lobby', lobby_type = lobby_type.lower(), lobby_id=lobby.id))
		#for lobby in Lobby.query.all():
		#	print(code)
		#	print(generateLobbyCode(lobby.id))
		#	if generateLobbyCode(lobby.id) == code:
		#		
		flash("Invalid code", 'warning')
		print(url_for('code', lobby_type = lobby_type))
		return redirect(url_for('code', lobby_type = lobby_type))
		
@socketio.on('join')
def on_join(data):
	room_id = data['room']
	print("Room id is {}".format(room_id))
	join_room(room_id)
	
	curr_lobby = handleQueryLobbyType(data['lobby type'], data['room'] // 10)
	if curr_lobby.user2 == None and current_user.id == curr_lobby.user1:
		emit("you first", room=room_id)
	if curr_lobby.user2 == None and current_user.id != curr_lobby.user1:
		handleLobbyUpdate(data['lobby type'], data['room'] // 10, current_user.id)
		curr_lobby = handleQueryLobbyType(data['lobby type'], data['room'] // 10)
		emit("start", {"user1" : handleQueryUser(curr_lobby.user1).username, "user2" : handleQueryUser(curr_lobby.user2).username},room=room_id)
		


@socketio.on('move')
def on_move(data):
	room_id = data['room']
	print(data['gameState'])
	data['gameState'] = "".join(data['gameState'])
	print(room_id)
	curr_lobby = handleQueryLobbyType(data['lobby type'], data['room'] // 10) #Lobby.query.filter_by(id=data['room'] // 10).first()
	for col in curr_lobby:
		print(col)
	handleStateUpdate(data['lobby type'], data['room'] // 10, data['gameState'])
	curr_lobby = handleQueryLobbyType(data['lobby type'], data['room'] // 10)
	p1 = User.query.filter_by(id=curr_lobby.user1).first()
	p2 = User.query.filter_by(id=curr_lobby.user2).first()
	emit("move", {'gameState' : curr_lobby.gameState, 'player' : [p1.username,p2.username][p1.username == data['player']]}, room = room_id)

@socketio.on('win')
def on_win(data):
	print("TEST HELLO PEDELI")
	user = User.query.filter_by(username=data['player']).first()
	if data["lobby type"] == "tictactoe":
		user.score_tictactoe += 1
	elif data["lobby type"] == "hangman":
		user.score_hangman += 1
	db_session.commit()
#prototip, oshte ne bachka
#@socketio.on('reset')
#def on_reset(data):
#	room_id = data['room']
#	emit('reset', room = room_id)

@socketio.on('leaving')
def on_disconnect(data):
	room_id = data['room']
	leave_room(room_id)
	emit('leaving', data, room=room_id)

if __name__ == '__main__':
	socketio.run(app)
