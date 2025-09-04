from sqlalchemy.orm import Session
from models import *
from schemas import *
import hashlib
import os

PASS_SALT=os.getenv("PASS_SALT")
if PASS_SALT is None:
    raise ValueError("Environment variable PASS_SALT is not set.")

#Function to get all users by their email
#Input: Email string
#Output: A user DTO
def get_user_by_email(db: Session, email: str) -> UserReadDTO:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return UserReadDTO(id=user.id, username=user.username, email=user.email, phone_number=user.phone_number)
    return None

#Function to get all users by their username
#Input: Username string
#Output: A user DTO
def get_user_by_username(db: Session, username: str) -> UserReadDTO:
    user = db.query(User).filter(User.username == username).first()
    if user:
        return UserReadDTO(id=user.id, username=user.username, email=user.email, phone_number=user.phone_number)
    return None

#Function to hash a password using hash 256 (no extra safety as argon2)
#Input: password string
#Output: hashed password string
def pass_hasher(password : str) -> str:
    hasher = hashlib.sha256()
    hasher.update((password + PASS_SALT).encode('utf-8'))
    return hasher.hexdigest()

#Function to create a generic user by DTOs
#Input: UserCreateDTO
#Output: UserReadDTO
def create_user(db: Session, userDTO: UserCreateDTO) -> UserReadDTO:
    #Hash password
    hashed_password = pass_hasher(userDTO.password)

    #Add user to db
    user = User(
        username=userDTO.username,
        email=userDTO.email,
        password=hashed_password,
        phone_number=userDTO.phone_number
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserReadDTO(id=user.id, username=user.username, email=user.email, phone_number=user.phone_number)

# Competition functions
def get_competition_by_id(db: Session, competition_id: str) -> CompetitionReadDTO:
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if competition:
        return CompetitionReadDTO(
            id=competition.id,
            name=competition.name,
            organizer=competition.organizer,
            invite_code=competition.invite_code,
            start_date=competition.start_date,
            end_date=competition.end_date
        )
    return None

def get_competition_by_invite_code(db: Session, invite_code: str) -> CompetitionReadDTO:
    competition = db.query(Competition).filter(Competition.invite_code == invite_code).first()
    if competition:
        return CompetitionReadDTO(
            id=competition.id,
            name=competition.name,
            organizer=competition.organizer,
            invite_code=competition.invite_code,
            start_date=competition.start_date,
            end_date=competition.end_date
        )
    return None

def create_competition(db: Session, competition_dto: CompetitionCreateDTO) -> CompetitionReadDTO:
    competition = Competition(
        name=competition_dto.name,
        organizer=competition_dto.organizer,
        invite_code=competition_dto.invite_code,
        start_date=competition_dto.start_date,
        end_date=competition_dto.end_date
    )
    db.add(competition)
    db.commit()
    db.refresh(competition)
    
    return CompetitionReadDTO(
        id=competition.id,
        name=competition.name,
        organizer=competition.organizer,
        invite_code=competition.invite_code,
        start_date=competition.start_date,
        end_date=competition.end_date
    )

def update_competition(db: Session, competition_id: str, competition_dto: CompetitionCreateDTO) -> CompetitionReadDTO:
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if not competition:
        return None
    
    competition.name = competition_dto.name
    competition.organizer = competition_dto.organizer
    competition.invite_code = competition_dto.invite_code
    competition.start_date = competition_dto.start_date
    competition.end_date = competition_dto.end_date
    
    db.commit()
    db.refresh(competition)
    
    return CompetitionReadDTO(
        id=competition.id,
        name=competition.name,
        organizer=competition.organizer,
        invite_code=competition.invite_code,
        start_date=competition.start_date,
        end_date=competition.end_date
    )

def delete_competition(db: Session, competition_id: str) -> bool:
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if not competition:
        return False
    
    db.delete(competition)
    db.commit()
    return True

# Exercise functions
def get_exercise_by_id(db: Session, exercise_id: str) -> ExerciseReadDTO:
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if exercise:
        return ExerciseReadDTO(
            id=exercise.id,
            link=exercise.link,
            name=exercise.name,
            score=exercise.score,
            difficulty=exercise.difficulty
        )
    return None

def create_exercise(db: Session, exercise_dto: ExerciseCreateDTO) -> ExerciseReadDTO:
    exercise = Exercise(
        link=exercise_dto.link,
        name=exercise_dto.name,
        score=exercise_dto.score,
        difficulty=exercise_dto.difficulty
    )
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    
    return ExerciseReadDTO(
        id=exercise.id,
        link=exercise.link,
        name=exercise.name,
        score=exercise.score,
        difficulty=exercise.difficulty
    )

def update_exercise(db: Session, exercise_id: str, exercise_dto: ExerciseCreateDTO) -> ExerciseReadDTO:
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return None
    
    exercise.link = exercise_dto.link
    exercise.name = exercise_dto.name
    exercise.score = exercise_dto.score
    exercise.difficulty = exercise_dto.difficulty
    
    db.commit()
    db.refresh(exercise)
    
    return ExerciseReadDTO(
        id=exercise.id,
        link=exercise.link,
        name=exercise.name,
        score=exercise.score,
        difficulty=exercise.difficulty
    )

def delete_exercise(db: Session, exercise_id: str) -> bool:
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return False
    
    db.delete(exercise)
    db.commit()
    return True

# Tag functions
def get_tag_by_id(db: Session, tag_id: str) -> TagReadDTO:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        return TagReadDTO(id=tag.id, type=tag.type)
    return None

def get_tag_by_type(db: Session, tag_type: str) -> TagReadDTO:
    tag = db.query(Tag).filter(Tag.type == tag_type).first()
    if tag:
        return TagReadDTO(id=tag.id, type=tag.type)
    return None

def create_tag(db: Session, tag_dto: TagCreateDTO) -> TagReadDTO:
    tag = Tag(type=tag_dto.type)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return TagReadDTO(id=tag.id, type=tag.type)

def update_tag(db: Session, tag_id: str, tag_dto: TagCreateDTO) -> TagReadDTO:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return None
    
    tag.type = tag_dto.type
    db.commit()
    db.refresh(tag)
    
    return TagReadDTO(id=tag.id, type=tag.type)

def delete_tag(db: Session, tag_id: str) -> bool:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return False
    
    db.delete(tag)
    db.commit()
    return True

# Team functions
def get_team_by_id(db: Session, team_id: str) -> TeamReadDTO:
    team = db.query(Team).filter(Team.id == team_id).first()
    if team:
        return TeamReadDTO(
            id=team.id,
            name=team.name,
            competition=team.competition,
            creator=team.creator,
            score=team.score
        )
    return None

def create_team(db: Session, team_dto: TeamCreateDTO) -> TeamReadDTO:
    team = Team(
        name=team_dto.name,
        competition=team_dto.competition,
        creator=team_dto.creator,
        score=team_dto.score
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    
    return TeamReadDTO(
        id=team.id,
        name=team.name,
        competition=team.competition,
        creator=team.creator,
        score=team.score
    )

def update_team(db: Session, team_id: str, team_dto: TeamCreateDTO) -> TeamReadDTO:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return None
    
    team.name = team_dto.name
    team.competition = team_dto.competition
    team.creator = team_dto.creator
    team.score = team_dto.score
    
    db.commit()
    db.refresh(team)
    
    return TeamReadDTO(
        id=team.id,
        name=team.name,
        competition=team.competition,
        creator=team.creator,
        score=team.score
    )

def delete_team(db: Session, team_id: str) -> bool:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return False
    
    db.delete(team)
    db.commit()
    return True

# Container functions
def get_container_by_id(db: Session, container_id: str) -> ContainerReadDTO:
    container = db.query(Container).filter(Container.id == container_id).first()
    if container:
        return ContainerReadDTO(id=container.id, deadline=container.deadline)
    return None

def create_container(db: Session, container_dto: ContainerCreateDTO) -> ContainerReadDTO:
    container = Container(deadline=container_dto.deadline)
    db.add(container)
    db.commit()
    db.refresh(container)
    
    return ContainerReadDTO(id=container.id, deadline=container.deadline)

def update_container(db: Session, container_id: str, container_dto: ContainerCreateDTO) -> ContainerReadDTO:
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        return None
    
    container.deadline = container_dto.deadline
    db.commit()
    db.refresh(container)
    
    return ContainerReadDTO(id=container.id, deadline=container.deadline)

def delete_container(db: Session, container_id: str) -> bool:
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        return False
    
    db.delete(container)
    db.commit()
    return True

# Relationship functions
# UserCompetition functions
def create_user_competition(db: Session, user_competition_dto: UserCompetitionCreateDTO) -> UserCompetitionCreateDTO:
    # Check if relationship already exists
    existing = db.query(UserCompetition).filter(
        UserCompetition.user_id == user_competition_dto.user_id,
        UserCompetition.competition_id == user_competition_dto.competition_id
    ).first()
    if existing:
        return None
    
    user_competition = UserCompetition(
        user_id=user_competition_dto.user_id,
        competition_id=user_competition_dto.competition_id
    )
    db.add(user_competition)
    db.commit()
    db.refresh(user_competition)
    
    return UserCompetitionCreateDTO(
        user_id=user_competition.user_id,
        competition_id=user_competition.competition_id
    )

def delete_user_competition(db: Session, user_id: str, competition_id: str) -> bool:
    user_competition = db.query(UserCompetition).filter(
        UserCompetition.user_id == user_id,
        UserCompetition.competition_id == competition_id
    ).first()
    if not user_competition:
        return False
    
    db.delete(user_competition)
    db.commit()
    return True

# UserTeam functions
def create_user_team(db: Session, user_team_dto: UserTeamCreateDTO) -> UserTeamCreateDTO:
    # Check if relationship already exists
    existing = db.query(UserTeam).filter(
        UserTeam.user_id == user_team_dto.user_id,
        UserTeam.team_id == user_team_dto.team_id
    ).first()
    if existing:
        return None
    
    user_team = UserTeam(
        user_id=user_team_dto.user_id,
        team_id=user_team_dto.team_id
    )
    db.add(user_team)
    db.commit()
    db.refresh(user_team)
    
    return UserTeamCreateDTO(
        user_id=user_team.user_id,
        team_id=user_team.team_id
    )

def delete_user_team(db: Session, user_id: str, team_id: str) -> bool:
    user_team = db.query(UserTeam).filter(
        UserTeam.user_id == user_id,
        UserTeam.team_id == team_id
    ).first()
    if not user_team:
        return False
    
    db.delete(user_team)
    db.commit()
    return True

# TeamCompetition functions
def create_team_competition(db: Session, team_competition_dto: TeamCompetitionCreateDTO) -> TeamCompetitionCreateDTO:
    # Check if relationship already exists
    existing = db.query(TeamCompetition).filter(
        TeamCompetition.team_id == team_competition_dto.team_id,
        TeamCompetition.competition_id == team_competition_dto.competition_id
    ).first()
    if existing:
        return None
    
    team_competition = TeamCompetition(
        team_id=team_competition_dto.team_id,
        competition_id=team_competition_dto.competition_id
    )
    db.add(team_competition)
    db.commit()
    db.refresh(team_competition)
    
    return TeamCompetitionCreateDTO(
        team_id=team_competition.team_id,
        competition_id=team_competition.competition_id
    )

def delete_team_competition(db: Session, team_id: str, competition_id: str) -> bool:
    team_competition = db.query(TeamCompetition).filter(
        TeamCompetition.team_id == team_id,
        TeamCompetition.competition_id == competition_id
    ).first()
    if not team_competition:
        return False
    
    db.delete(team_competition)
    db.commit()
    return True

# ExerciseTag functions
def create_exercise_tag(db: Session, exercise_tag_dto: ExerciseTagCreateDTO) -> ExerciseTagCreateDTO:
    # Check if relationship already exists
    existing = db.query(ExerciseTag).filter(
        ExerciseTag.exercise_id == exercise_tag_dto.exercise_id,
        ExerciseTag.tag_id == exercise_tag_dto.tag_id
    ).first()
    if existing:
        return None
    
    exercise_tag = ExerciseTag(
        exercise_id=exercise_tag_dto.exercise_id,
        tag_id=exercise_tag_dto.tag_id
    )
    db.add(exercise_tag)
    db.commit()
    db.refresh(exercise_tag)
    
    return ExerciseTagCreateDTO(
        exercise_id=exercise_tag.exercise_id,
        tag_id=exercise_tag.tag_id
    )

def delete_exercise_tag(db: Session, exercise_id: str, tag_id: str) -> bool:
    exercise_tag = db.query(ExerciseTag).filter(
        ExerciseTag.exercise_id == exercise_id,
        ExerciseTag.tag_id == tag_id
    ).first()
    if not exercise_tag:
        return False
    
    db.delete(exercise_tag)
    db.commit()
    return True

# ExerciseCompetition functions
def create_exercise_competition(db: Session, exercise_competition_dto: ExerciseCompetitionCreateDTO) -> ExerciseCompetitionCreateDTO:
    # Check if relationship already exists
    existing = db.query(ExerciseCompetition).filter(
        ExerciseCompetition.exercise_id == exercise_competition_dto.exercise_id,
        ExerciseCompetition.competition_id == exercise_competition_dto.competition_id
    ).first()
    if existing:
        return None
    
    exercise_competition = ExerciseCompetition(
        exercise_id=exercise_competition_dto.exercise_id,
        competition_id=exercise_competition_dto.competition_id
    )
    db.add(exercise_competition)
    db.commit()
    db.refresh(exercise_competition)
    
    return ExerciseCompetitionCreateDTO(
        exercise_id=exercise_competition.exercise_id,
        competition_id=exercise_competition.competition_id
    )

def delete_exercise_competition(db: Session, exercise_id: str, competition_id: str) -> bool:
    exercise_competition = db.query(ExerciseCompetition).filter(
        ExerciseCompetition.exercise_id == exercise_id,
        ExerciseCompetition.competition_id == competition_id
    ).first()
    if not exercise_competition:
        return False
    
    db.delete(exercise_competition)
    db.commit()
    return True

# ContainerCompetition functions
def create_container_competition(db: Session, container_competition_dto: ContainerCompetitionCreateDTO) -> ContainerCompetitionCreateDTO:
    # Check if relationship already exists
    existing = db.query(ContainerCompetition).filter(
        ContainerCompetition.container_id == container_competition_dto.container_id,
        ContainerCompetition.competition_id == container_competition_dto.competition_id
    ).first()
    if existing:
        return None
    
    container_competition = ContainerCompetition(
        container_id=container_competition_dto.container_id,
        competition_id=container_competition_dto.competition_id
    )
    db.add(container_competition)
    db.commit()
    db.refresh(container_competition)
    
    return ContainerCompetitionCreateDTO(
        container_id=container_competition.container_id,
        competition_id=container_competition.competition_id
    )

def delete_container_competition(db: Session, container_id: str, competition_id: str) -> bool:
    container_competition = db.query(ContainerCompetition).filter(
        ContainerCompetition.container_id == container_id,
        ContainerCompetition.competition_id == competition_id
    ).first()
    if not container_competition:
        return False
    
    db.delete(container_competition)
    db.commit()
    return True