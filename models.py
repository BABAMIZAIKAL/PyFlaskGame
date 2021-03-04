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
        
class Lobby(Base):
	__tablename__ = 'lobby'
	id = Column(Integer, primary_key=True)
	user1 = Column(String(250), unique=True, nullable=False)
	user2 = Column(String(250), unique=True, nullable=True)

