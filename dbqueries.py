from database import db_session, init_db
from sqlalchemy import text
from login import login_manager
from models import User, Lobby, TicTacToeLobby, HangmanLobby, CAHLobby


# SQL queries
def handleUpdateCAHUser(user, lobby_id, user_id):
    db_session.execute(
        text("update " + "cahlobby" + " set user" + str(user) + " = " + str(user_id) + " where id = " + str(
            lobby_id) + ";"))
    db_session.commit()


def handleQueryLobbyType(lobbyType, id):
    curr_lobby = db_session.execute(
        text("select * from " + lobbyType + "lobby" + " where id = " + str(id) + " limit 1;")).first()
    return curr_lobby


def handleCreateLobbyType(lobbyType, data):
    lobby = None
    if lobbyType == "tictactoe":
        lobby = TicTacToeLobby(user1=data[0], gameState=data[2])
    elif lobbyType == "hangman":
        lobby = HangmanLobby(user1=data[0], gameState=data[2])
    else:
        lobby = CAHLobby(user1=data[0], gameState="asdf")
    # lobby = db_session.execute("insert into " + lobbyType + "lobby(user1, user2, gameState)" + " values(" + ", ".join(str(a) for a in data) + ") returning *;"))
    db_session.add(lobby)
    db_session.commit()
    return lobby.id


def handleStateUpdate(lobbyType, id, newState):
    db_session.execute(
        text("update " + lobbyType + "lobby" + " set gameState = \"" + newState + "\" where id = " + str(id) + ";"))
    db_session.commit()


def handleLobbyUpdate(lobbyType, id, id2):
    print(id2)
    db_session.execute(
        text("update " + lobbyType + "lobby" + " set user2 = " + str(id2) + " where id = " + str(id) + ";"))
    db_session.commit()


def handleQueryUser(id):
    return db_session.execute(text("select * from users where id = " + str(id) + ";")).first()
