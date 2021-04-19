from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, aliased
from sqlalchemy.sql.expression import func
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    login_id = Column(String(36), nullable=True)
    score_tictactoe = Column(Integer, unique=False, nullable=False, default=0)
    score_hangman = Column(Integer, unique=False, nullable=False, default=0)
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<User %r>' % self.username
        
    def get_id(self):
    	return self.login_id
    
    def get_id_2(self):
        return self.id
            
class Lobby(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    user1 = Column(Integer, unique=False, nullable=False)
    user2 = Column(Integer, unique=False, nullable=True)
    gameState = Column(String(100), unique=False, nullable=False)
    #currentPlayer = Column(Integer, unique=False, nullable=False)
    #lobbyType = Column(String(100), unique=True, nullable=False)
    
    
class TicTacToeLobby(Lobby):
    __tablename__ = 'tictactoelobby'
    
    
class HangmanLobby(Lobby):
    __tablename__ = 'hangmanlobby'
