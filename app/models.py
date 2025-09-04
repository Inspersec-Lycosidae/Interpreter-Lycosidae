# models.py
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, Time, ForeignKey, CheckConstraint, UniqueConstraint, SmallInteger, Boolean
)
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()

######################################################################
##### Uses SqlAlchemy bases for static objects; referenced in DB #####
######################################################################

class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(60), nullable=False, unique=True)
    email = Column(String(45), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
    phone_number = Column(String(20), nullable=True)
    is_admin = Column(Boolean, default=False)

class Competition(Base):
    __tablename__ = 'competitions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    organizer = Column(String(100), nullable=False)
    invite_code = Column(String(20), nullable=False, unique=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    link = Column(String(500), nullable=False)
    name = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    difficulty = Column(String(20), nullable=False)

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(50), nullable=False, unique=True)

class Team(Base):
    __tablename__ = 'teams'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    competition = Column(String(36), ForeignKey('competitions.id'), nullable=False)
    creator = Column(String(36), ForeignKey('users.id'), nullable=False)
    score = Column(Integer, default=0)

class Container(Base):
    __tablename__ = 'containers'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deadline = Column(DateTime, nullable=False)

# Relationship tables
class UserCompetition(Base):
    __tablename__ = 'user_competitions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    competition_id = Column(String(36), ForeignKey('competitions.id'), nullable=False)

class UserTeam(Base):
    __tablename__ = 'user_teams'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    team_id = Column(String(36), ForeignKey('teams.id'), nullable=False)

class TeamCompetition(Base):
    __tablename__ = 'team_competitions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey('teams.id'), nullable=False)
    competition_id = Column(String(36), ForeignKey('competitions.id'), nullable=False)

class ExerciseTag(Base):
    __tablename__ = 'exercise_tags'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exercise_id = Column(String(36), ForeignKey('exercises.id'), nullable=False)
    tag_id = Column(String(36), ForeignKey('tags.id'), nullable=False)

class ExerciseCompetition(Base):
    __tablename__ = 'exercise_competitions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    exercise_id = Column(String(36), ForeignKey('exercises.id'), nullable=False)
    competition_id = Column(String(36), ForeignKey('competitions.id'), nullable=False)

class ContainerCompetition(Base):
    __tablename__ = 'container_competitions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    container_id = Column(String(36), ForeignKey('containers.id'), nullable=False)
    competition_id = Column(String(36), ForeignKey('competitions.id'), nullable=False)