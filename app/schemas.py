# schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

#########################################################################
##### Uses pydantic for cache/dynamic objects; not referenced in DB #####
#########################################################################

#Base JWT AuthToken model
class AuthToken(BaseModel):
    id : str
    username : str
    email : str
    role : Optional[str] = None
    exp : Optional[int] = None

    class Config:
        extra = "allow"

# User DTOs
class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None

class UserReadDTO(BaseModel):
    id: str
    username: str
    email: EmailStr
    phone_number: Optional[str] = None

# Competition DTOs
class CompetitionCreateDTO(BaseModel):
    name: str
    organizer: str
    invite_code: str
    start_date: datetime
    end_date: datetime

class CompetitionReadDTO(BaseModel):
    id: str
    name: str
    organizer: str
    invite_code: str
    start_date: datetime
    end_date: datetime

# Exercise DTOs
class ExerciseCreateDTO(BaseModel):
    link: str
    name: str
    score: int
    difficulty: str

class ExerciseReadDTO(BaseModel):
    id: str
    link: str
    name: str
    score: int
    difficulty: str

# Tag DTOs
class TagCreateDTO(BaseModel):
    type: str

class TagReadDTO(BaseModel):
    id: str
    type: str

# Team DTOs
class TeamCreateDTO(BaseModel):
    name: str
    competition: str
    creator: str
    score: Optional[int] = 0

class TeamReadDTO(BaseModel):
    id: str
    name: str
    competition: str
    creator: str
    score: int

# Container DTOs
class ContainerCreateDTO(BaseModel):
    deadline: datetime

class ContainerReadDTO(BaseModel):
    id: str
    deadline: datetime

# Relationship DTOs
class UserCompetitionCreateDTO(BaseModel):
    user_id: str
    competition_id: str

class UserTeamCreateDTO(BaseModel):
    user_id: str
    team_id: str

class TeamCompetitionCreateDTO(BaseModel):
    team_id: str
    competition_id: str

class ExerciseTagCreateDTO(BaseModel):
    exercise_id: str
    tag_id: str

class ExerciseCompetitionCreateDTO(BaseModel):
    exercise_id: str
    competition_id: str

class ContainerCompetitionCreateDTO(BaseModel):
    container_id: str
    competition_id: str