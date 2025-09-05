from sqlalchemy.orm import Session
from models import *
from schemas import *
import hashlib
import os
import time
from logger import get_structured_logger

PASS_SALT=os.getenv("PASS_SALT")
if PASS_SALT is None:
    raise ValueError("Environment variable PASS_SALT is not set.")

db_logger = get_structured_logger("database")

def get_user_by_email(db: Session, email: str) -> UserReadDTO:
    """
    Busca um usuário pelo email
    """
    user = db.query(User).filter(User.email == email).first()
    if user:
        return UserReadDTO(id=user.id, username=user.username, email=user.email, phone_number=user.phone_number)
    return None

def get_user_by_username(db: Session, username: str) -> UserReadDTO:
    """
    Busca um usuário pelo username
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        return UserReadDTO(id=user.id, username=user.username, email=user.email, phone_number=user.phone_number)
    return None

def get_user_by_id(db: Session, user_id: str) -> UserReadDTO:
    """
    Busca um usuário pelo ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return UserReadDTO(id=user.id, username=user.username, email=user.email, phone_number=user.phone_number)
    return None

def pass_hasher(password : str) -> str:
    """
    Gera hash da senha usando SHA-256 com salt
    """
    hasher = hashlib.sha256()
    hasher.update((password + PASS_SALT).encode('utf-8'))
    return hasher.hexdigest()

def create_user(db: Session, userDTO: UserCreateDTO) -> UserReadDTO:
    """
    Cria um novo usuário no banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de usuário no banco de dados", 
                   email=userDTO.email, 
                   username=userDTO.username)
    
    try:
        hashed_password = pass_hasher(userDTO.password)
        db_logger.debug("Senha hashada com sucesso", email=userDTO.email)
        user = User(
            username=userDTO.username,
            email=userDTO.email,
            password=hashed_password,
            phone_number=userDTO.phone_number
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        duration = time.time() - start_time
        db_logger.log_database("CREATE", "users", duration, 
                              user_id=user.id,
                              email=user.email,
                              username=user.username)

        return UserReadDTO(id=user.id, username=user.username, email=user.email, phone_number=user.phone_number)
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar usuário no banco de dados", 
                       error=str(e),
                       email=userDTO.email,
                       username=userDTO.username,
                       duration_ms=round(duration * 1000, 2))
        raise e

def get_competition_by_id(db: Session, competition_id: str) -> CompetitionReadDTO:
    """
    Busca uma competição pelo ID
    """
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if competition:
        return CompetitionReadDTO(
            id=competition.id,
            name=competition.name,
            organizer=competition.organizer,
            invite_code=competition.invite_code,
            start_date=competition.start_date.isoformat(),
            end_date=competition.end_date.isoformat()
        )
    return None

def get_competition_by_invite_code(db: Session, invite_code: str) -> CompetitionReadDTO:
    """
    Busca uma competição pelo código de convite
    """
    competition = db.query(Competition).filter(Competition.invite_code == invite_code).first()
    if competition:
        return CompetitionReadDTO(
            id=competition.id,
            name=competition.name,
            organizer=competition.organizer,
            invite_code=competition.invite_code,
            start_date=competition.start_date.isoformat(),
            end_date=competition.end_date.isoformat()
        )
    return None

def create_competition(db: Session, competition_dto: CompetitionCreateDTO) -> CompetitionReadDTO:
    """
    Cria uma nova competição no banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de competição no banco de dados", 
                   name=competition_dto.name,
                   organizer=competition_dto.organizer,
                   invite_code=competition_dto.invite_code)
    
    try:
        # Converter strings de data para objetos datetime
        from datetime import datetime
        start_date = datetime.fromisoformat(competition_dto.start_date.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(competition_dto.end_date.replace('Z', '+00:00'))
        
        competition = Competition(
            name=competition_dto.name,
            organizer=competition_dto.organizer,
            invite_code=competition_dto.invite_code,
            start_date=start_date,
            end_date=end_date
        )
        db.add(competition)
        db.commit()
        db.refresh(competition)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "competitions", duration, 
                              competition_id=competition.id,
                              name=competition.name,
                              organizer=competition.organizer)
        
        return CompetitionReadDTO(
            id=competition.id,
            name=competition.name,
            organizer=competition.organizer,
            invite_code=competition.invite_code,
            start_date=competition.start_date.isoformat(),
            end_date=competition.end_date.isoformat()
        )
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar competição no banco de dados", 
                       error=str(e),
                       name=competition_dto.name,
                       organizer=competition_dto.organizer,
                       duration_ms=round(duration * 1000, 2))
        raise e

def update_competition(db: Session, competition_id: str, competition_dto: CompetitionCreateDTO) -> CompetitionReadDTO:
    """
    Atualiza uma competição existente
    """
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if not competition:
        return None
    
    # Converter strings de data para objetos datetime
    from datetime import datetime
    start_date = datetime.fromisoformat(competition_dto.start_date.replace('Z', '+00:00'))
    end_date = datetime.fromisoformat(competition_dto.end_date.replace('Z', '+00:00'))
    
    competition.name = competition_dto.name
    competition.organizer = competition_dto.organizer
    competition.invite_code = competition_dto.invite_code
    competition.start_date = start_date
    competition.end_date = end_date
    
    db.commit()
    db.refresh(competition)
    
    return CompetitionReadDTO(
        id=competition.id,
        name=competition.name,
        organizer=competition.organizer,
        invite_code=competition.invite_code,
        start_date=competition.start_date.isoformat(),
        end_date=competition.end_date.isoformat()
    )

def delete_competition(db: Session, competition_id: str) -> bool:
    """
    Deleta uma competição do banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de competição no banco de dados", 
                   competition_id=competition_id)
    
    try:
        competition = db.query(Competition).filter(Competition.id == competition_id).first()
        if not competition:
            db_logger.warning("Tentativa de deletar competição inexistente", 
                             competition_id=competition_id)
            return False
        
        db.delete(competition)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "competitions", duration, 
                              competition_id=competition_id,
                              name=competition.name)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar competição no banco de dados", 
                       error=str(e),
                       competition_id=competition_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def get_exercise_by_id(db: Session, exercise_id: str) -> ExerciseReadDTO:
    """
    Busca um exercício pelo ID
    """
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if exercise:
        return ExerciseReadDTO(
            id=exercise.id,
            link=exercise.link,
            name=exercise.name,
            score=exercise.score,
            difficulty=exercise.difficulty,
            port=exercise.port
        )
    return None

def create_exercise(db: Session, exercise_dto: ExerciseCreateDTO) -> ExerciseReadDTO:
    """
    Cria um novo exercício no banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de exercício no banco de dados", 
                   name=exercise_dto.name,
                   difficulty=exercise_dto.difficulty)
    
    try:
        exercise = Exercise(
            link=exercise_dto.link,
            name=exercise_dto.name,
            score=exercise_dto.score,
            difficulty=exercise_dto.difficulty,
            port=exercise_dto.port
        )
        db.add(exercise)
        db.commit()
        db.refresh(exercise)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "exercises", duration, 
                              exercise_id=exercise.id,
                              name=exercise.name,
                              difficulty=exercise.difficulty)
        
        return ExerciseReadDTO(
            id=exercise.id,
            link=exercise.link,
            name=exercise.name,
            score=exercise.score,
            difficulty=exercise.difficulty,
            port=exercise.port
        )
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar exercício no banco de dados", 
                       error=str(e),
                       name=exercise_dto.name,
                       difficulty=exercise_dto.difficulty,
                       duration_ms=round(duration * 1000, 2))
        raise e

def update_exercise(db: Session, exercise_id: str, exercise_dto: ExerciseCreateDTO) -> ExerciseReadDTO:
    """
    Atualiza um exercício existente
    """
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return None
    
    exercise.link = exercise_dto.link
    exercise.name = exercise_dto.name
    exercise.score = exercise_dto.score
    exercise.difficulty = exercise_dto.difficulty
    exercise.port = exercise_dto.port
    
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
    """
    Deleta um exercício do banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de exercício no banco de dados", 
                   exercise_id=exercise_id)
    
    try:
        exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
        if not exercise:
            db_logger.warning("Tentativa de deletar exercício inexistente", 
                             exercise_id=exercise_id)
            return False
        
        db.delete(exercise)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "exercises", duration, 
                              exercise_id=exercise_id,
                              name=exercise.name)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar exercício no banco de dados", 
                       error=str(e),
                       exercise_id=exercise_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def get_tag_by_id(db: Session, tag_id: str) -> TagReadDTO:
    """
    Busca uma tag pelo ID
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if tag:
        return TagReadDTO(id=tag.id, type=tag.type)
    return None

def get_tag_by_type(db: Session, tag_type: str) -> TagReadDTO:
    """
    Busca uma tag pelo tipo
    """
    tag = db.query(Tag).filter(Tag.type == tag_type).first()
    if tag:
        return TagReadDTO(id=tag.id, type=tag.type)
    return None

def create_tag(db: Session, tag_dto: TagCreateDTO) -> TagReadDTO:
    """
    Cria uma nova tag no banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de tag no banco de dados", 
                   type=tag_dto.type)
    
    try:
        tag = Tag(type=tag_dto.type)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "tags", duration, 
                              tag_id=tag.id,
                              type=tag.type)
        
        return TagReadDTO(id=tag.id, type=tag.type)
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar tag no banco de dados", 
                       error=str(e),
                       type=tag_dto.type,
                       duration_ms=round(duration * 1000, 2))
        raise e

def update_tag(db: Session, tag_id: str, tag_dto: TagCreateDTO) -> TagReadDTO:
    """
    Atualiza uma tag existente
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        return None
    
    tag.type = tag_dto.type
    db.commit()
    db.refresh(tag)
    
    return TagReadDTO(id=tag.id, type=tag.type)

def delete_tag(db: Session, tag_id: str) -> bool:
    """
    Deleta uma tag do banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de tag no banco de dados", 
                   tag_id=tag_id)
    
    try:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            db_logger.warning("Tentativa de deletar tag inexistente", 
                             tag_id=tag_id)
            return False
        
        db.delete(tag)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "tags", duration, 
                              tag_id=tag_id,
                              type=tag.type)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar tag no banco de dados", 
                       error=str(e),
                       tag_id=tag_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def get_team_by_id(db: Session, team_id: str) -> TeamReadDTO:
    """
    Busca um time pelo ID
    """
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
    """
    Cria um novo time no banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de time no banco de dados", 
                   name=team_dto.name,
                   competition=team_dto.competition)
    
    try:
        team = Team(
            name=team_dto.name,
            competition=team_dto.competition,
            creator=team_dto.creator,
            score=team_dto.score
        )
        db.add(team)
        db.commit()
        db.refresh(team)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "teams", duration, 
                              team_id=team.id,
                              name=team.name,
                              competition=team.competition)
        
        return TeamReadDTO(
            id=team.id,
            name=team.name,
            competition=team.competition,
            creator=team.creator,
            score=team.score
        )
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar time no banco de dados", 
                       error=str(e),
                       name=team_dto.name,
                       competition=team_dto.competition,
                       duration_ms=round(duration * 1000, 2))
        raise e

def update_team(db: Session, team_id: str, team_dto: TeamCreateDTO) -> TeamReadDTO:
    """
    Atualiza um time existente
    """
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
    """
    Deleta um time do banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de time no banco de dados", 
                   team_id=team_id)
    
    try:
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            db_logger.warning("Tentativa de deletar time inexistente", 
                             team_id=team_id)
            return False
        
        db.delete(team)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "teams", duration, 
                              team_id=team_id,
                              name=team.name)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar time no banco de dados", 
                       error=str(e),
                       team_id=team_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def get_container_by_id(db: Session, container_id: str) -> ContainerReadDTO:
    """
    Busca um container pelo ID
    """
    container = db.query(Container).filter(Container.id == container_id).first()
    if container:
        return ContainerReadDTO(id=container.id, deadline=container.deadline.isoformat())
    return None

def create_container(db: Session, container_dto: ContainerCreateDTO) -> ContainerReadDTO:
    """
    Cria um novo container no banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de container no banco de dados", 
                   deadline=container_dto.deadline)
    
    try:
        # Converter string de data para objeto datetime
        from datetime import datetime
        deadline = datetime.fromisoformat(container_dto.deadline.replace('Z', '+00:00'))
        
        container = Container(deadline=deadline)
        db.add(container)
        db.commit()
        db.refresh(container)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "containers", duration, 
                              container_id=container.id,
                              deadline=container.deadline.isoformat())
        
        return ContainerReadDTO(id=container.id, deadline=container.deadline.isoformat())
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar container no banco de dados", 
                       error=str(e),
                       deadline=container_dto.deadline,
                       duration_ms=round(duration * 1000, 2))
        raise e

def update_container(db: Session, container_id: str, container_dto: ContainerCreateDTO) -> ContainerReadDTO:
    """
    Atualiza um container existente
    """
    container = db.query(Container).filter(Container.id == container_id).first()
    if not container:
        return None
    
    # Converter string de data para objeto datetime
    from datetime import datetime
    deadline = datetime.fromisoformat(container_dto.deadline.replace('Z', '+00:00'))
    
    container.deadline = deadline
    db.commit()
    db.refresh(container)
    
    return ContainerReadDTO(id=container.id, deadline=container.deadline.isoformat())

def delete_container(db: Session, container_id: str) -> bool:
    """
    Deleta um container do banco de dados
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de container no banco de dados", 
                   container_id=container_id)
    
    try:
        container = db.query(Container).filter(Container.id == container_id).first()
        if not container:
            db_logger.warning("Tentativa de deletar container inexistente", 
                             container_id=container_id)
            return False
        
        db.delete(container)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "containers", duration, 
                              container_id=container_id,
                              deadline=container.deadline.isoformat())
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar container no banco de dados", 
                       error=str(e),
                       container_id=container_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def create_user_competition(db: Session, user_competition_dto: UserCompetitionCreateDTO) -> UserCompetitionCreateDTO:
    """
    Cria um relacionamento usuário-competição
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de relacionamento usuário-competição", 
                   user_id=user_competition_dto.user_id,
                   competition_id=user_competition_dto.competition_id)
    
    try:
        existing = db.query(UserCompetition).filter(
            UserCompetition.user_id == user_competition_dto.user_id,
            UserCompetition.competition_id == user_competition_dto.competition_id
        ).first()
        if existing:
            db_logger.warning("Relacionamento usuário-competição já existe", 
                             user_id=user_competition_dto.user_id,
                             competition_id=user_competition_dto.competition_id)
            return None
        
        user_competition = UserCompetition(
            user_id=user_competition_dto.user_id,
            competition_id=user_competition_dto.competition_id
        )
        db.add(user_competition)
        db.commit()
        db.refresh(user_competition)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "user_competitions", duration, 
                              user_id=user_competition.user_id,
                              competition_id=user_competition.competition_id)
        
        return UserCompetitionCreateDTO(
            user_id=user_competition.user_id,
            competition_id=user_competition.competition_id
        )
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar relacionamento usuário-competição", 
                       error=str(e),
                       user_id=user_competition_dto.user_id,
                       competition_id=user_competition_dto.competition_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def delete_user_competition(db: Session, user_id: str, competition_id: str) -> bool:
    """
    Deleta um relacionamento usuário-competição
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de relacionamento usuário-competição", 
                   user_id=user_id,
                   competition_id=competition_id)
    
    try:
        user_competition = db.query(UserCompetition).filter(
            UserCompetition.user_id == user_id,
            UserCompetition.competition_id == competition_id
        ).first()
        if not user_competition:
            db_logger.warning("Relacionamento usuário-competição não encontrado", 
                             user_id=user_id,
                             competition_id=competition_id)
            return False
        
        db.delete(user_competition)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "user_competitions", duration, 
                              user_id=user_id,
                              competition_id=competition_id)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar relacionamento usuário-competição", 
                       error=str(e),
                       user_id=user_id,
                       competition_id=competition_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def create_user_team(db: Session, user_team_dto: UserTeamCreateDTO) -> UserTeamCreateDTO:
    """
    Cria um relacionamento usuário-time
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de relacionamento usuário-time", 
                   user_id=user_team_dto.user_id,
                   team_id=user_team_dto.team_id)
    
    try:
        existing = db.query(UserTeam).filter(
            UserTeam.user_id == user_team_dto.user_id,
            UserTeam.team_id == user_team_dto.team_id
        ).first()
        if existing:
            db_logger.warning("Relacionamento usuário-time já existe", 
                             user_id=user_team_dto.user_id,
                             team_id=user_team_dto.team_id)
            return None
        
        user_team = UserTeam(
            user_id=user_team_dto.user_id,
            team_id=user_team_dto.team_id
        )
        db.add(user_team)
        db.commit()
        db.refresh(user_team)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "user_teams", duration, 
                              user_id=user_team.user_id,
                              team_id=user_team.team_id)
        
        return UserTeamCreateDTO(
            user_id=user_team.user_id,
            team_id=user_team.team_id
        )
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar relacionamento usuário-time", 
                       error=str(e),
                       user_id=user_team_dto.user_id,
                       team_id=user_team_dto.team_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def delete_user_team(db: Session, user_id: str, team_id: str) -> bool:
    """
    Deleta um relacionamento usuário-time
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de relacionamento usuário-time", 
                   user_id=user_id,
                   team_id=team_id)
    
    try:
        user_team = db.query(UserTeam).filter(
            UserTeam.user_id == user_id,
            UserTeam.team_id == team_id
        ).first()
        if not user_team:
            db_logger.warning("Relacionamento usuário-time não encontrado", 
                             user_id=user_id,
                             team_id=team_id)
            return False
        
        db.delete(user_team)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "user_teams", duration, 
                              user_id=user_id,
                              team_id=team_id)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar relacionamento usuário-time", 
                       error=str(e),
                       user_id=user_id,
                       team_id=team_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def create_team_competition(db: Session, team_competition_dto: TeamCompetitionCreateDTO) -> TeamCompetitionCreateDTO:
    """
    Cria um relacionamento time-competição
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de relacionamento time-competição", 
                   team_id=team_competition_dto.team_id,
                   competition_id=team_competition_dto.competition_id)
    
    try:
        existing = db.query(TeamCompetition).filter(
            TeamCompetition.team_id == team_competition_dto.team_id,
            TeamCompetition.competition_id == team_competition_dto.competition_id
        ).first()
        if existing:
            db_logger.warning("Relacionamento time-competição já existe", 
                             team_id=team_competition_dto.team_id,
                             competition_id=team_competition_dto.competition_id)
            return None
        
        team_competition = TeamCompetition(
            team_id=team_competition_dto.team_id,
            competition_id=team_competition_dto.competition_id
        )
        db.add(team_competition)
        db.commit()
        db.refresh(team_competition)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "team_competitions", duration, 
                              team_id=team_competition.team_id,
                              competition_id=team_competition.competition_id)
        
        return TeamCompetitionCreateDTO(
            team_id=team_competition.team_id,
            competition_id=team_competition.competition_id
        )
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar relacionamento time-competição", 
                       error=str(e),
                       team_id=team_competition_dto.team_id,
                       competition_id=team_competition_dto.competition_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def delete_team_competition(db: Session, team_id: str, competition_id: str) -> bool:
    """
    Deleta um relacionamento time-competição
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de relacionamento time-competição", 
                   team_id=team_id,
                   competition_id=competition_id)
    
    try:
        team_competition = db.query(TeamCompetition).filter(
            TeamCompetition.team_id == team_id,
            TeamCompetition.competition_id == competition_id
        ).first()
        if not team_competition:
            db_logger.warning("Relacionamento time-competição não encontrado", 
                             team_id=team_id,
                             competition_id=competition_id)
            return False
        
        db.delete(team_competition)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "team_competitions", duration, 
                              team_id=team_id,
                              competition_id=competition_id)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar relacionamento time-competição", 
                       error=str(e),
                       team_id=team_id,
                       competition_id=competition_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def create_exercise_tag(db: Session, exercise_tag_dto: ExerciseTagCreateDTO) -> ExerciseTagCreateDTO:
    """
    Cria um relacionamento exercício-tag
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de relacionamento exercício-tag", 
                   exercise_id=exercise_tag_dto.exercise_id,
                   tag_id=exercise_tag_dto.tag_id)
    
    try:
        existing = db.query(ExerciseTag).filter(
            ExerciseTag.exercise_id == exercise_tag_dto.exercise_id,
            ExerciseTag.tag_id == exercise_tag_dto.tag_id
        ).first()
        if existing:
            db_logger.warning("Relacionamento exercício-tag já existe", 
                             exercise_id=exercise_tag_dto.exercise_id,
                             tag_id=exercise_tag_dto.tag_id)
            return None
        
        exercise_tag = ExerciseTag(
            exercise_id=exercise_tag_dto.exercise_id,
            tag_id=exercise_tag_dto.tag_id
        )
        db.add(exercise_tag)
        db.commit()
        db.refresh(exercise_tag)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "exercise_tags", duration, 
                              exercise_id=exercise_tag.exercise_id,
                              tag_id=exercise_tag.tag_id)
        
        return ExerciseTagCreateDTO(
            exercise_id=exercise_tag.exercise_id,
            tag_id=exercise_tag.tag_id
        )
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar relacionamento exercício-tag", 
                       error=str(e),
                       exercise_id=exercise_tag_dto.exercise_id,
                       tag_id=exercise_tag_dto.tag_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def delete_exercise_tag(db: Session, exercise_id: str, tag_id: str) -> bool:
    """
    Deleta um relacionamento exercício-tag
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de relacionamento exercício-tag", 
                   exercise_id=exercise_id,
                   tag_id=tag_id)
    
    try:
        exercise_tag = db.query(ExerciseTag).filter(
            ExerciseTag.exercise_id == exercise_id,
            ExerciseTag.tag_id == tag_id
        ).first()
        if not exercise_tag:
            db_logger.warning("Relacionamento exercício-tag não encontrado", 
                             exercise_id=exercise_id,
                             tag_id=tag_id)
            return False
        
        db.delete(exercise_tag)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "exercise_tags", duration, 
                              exercise_id=exercise_id,
                              tag_id=tag_id)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar relacionamento exercício-tag", 
                       error=str(e),
                       exercise_id=exercise_id,
                       tag_id=tag_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def create_exercise_competition(db: Session, exercise_competition_dto: ExerciseCompetitionCreateDTO) -> ExerciseCompetitionCreateDTO:
    """
    Cria um relacionamento exercício-competição
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de relacionamento exercício-competição", 
                   exercise_id=exercise_competition_dto.exercise_id,
                   competition_id=exercise_competition_dto.competition_id)
    
    try:
        existing = db.query(ExerciseCompetition).filter(
            ExerciseCompetition.exercise_id == exercise_competition_dto.exercise_id,
            ExerciseCompetition.competition_id == exercise_competition_dto.competition_id
        ).first()
        if existing:
            db_logger.warning("Relacionamento exercício-competição já existe", 
                             exercise_id=exercise_competition_dto.exercise_id,
                             competition_id=exercise_competition_dto.competition_id)
            return None
        
        exercise_competition = ExerciseCompetition(
            exercise_id=exercise_competition_dto.exercise_id,
            competition_id=exercise_competition_dto.competition_id
        )
        db.add(exercise_competition)
        db.commit()
        db.refresh(exercise_competition)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "exercise_competitions", duration, 
                              exercise_id=exercise_competition.exercise_id,
                              competition_id=exercise_competition.competition_id)
        
        return ExerciseCompetitionCreateDTO(
            exercise_id=exercise_competition.exercise_id,
            competition_id=exercise_competition.competition_id
        )
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar relacionamento exercício-competição", 
                       error=str(e),
                       exercise_id=exercise_competition_dto.exercise_id,
                       competition_id=exercise_competition_dto.competition_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def delete_exercise_competition(db: Session, exercise_id: str, competition_id: str) -> bool:
    """
    Deleta um relacionamento exercício-competição
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de relacionamento exercício-competição", 
                   exercise_id=exercise_id,
                   competition_id=competition_id)
    
    try:
        exercise_competition = db.query(ExerciseCompetition).filter(
            ExerciseCompetition.exercise_id == exercise_id,
            ExerciseCompetition.competition_id == competition_id
        ).first()
        if not exercise_competition:
            db_logger.warning("Relacionamento exercício-competição não encontrado", 
                             exercise_id=exercise_id,
                             competition_id=competition_id)
            return False
        
        db.delete(exercise_competition)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "exercise_competitions", duration, 
                              exercise_id=exercise_id,
                              competition_id=competition_id)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar relacionamento exercício-competição", 
                       error=str(e),
                       exercise_id=exercise_id,
                       competition_id=competition_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def create_container_competition(db: Session, container_competition_dto: ContainerCompetitionCreateDTO) -> ContainerCompetitionCreateDTO:
    """
    Cria um relacionamento container-competição
    """
    start_time = time.time()
    db_logger.info("Iniciando criação de relacionamento container-competição", 
                   container_id=container_competition_dto.container_id,
                   competition_id=container_competition_dto.competition_id)
    
    try:
        existing = db.query(ContainerCompetition).filter(
            ContainerCompetition.container_id == container_competition_dto.container_id,
            ContainerCompetition.competition_id == container_competition_dto.competition_id
        ).first()
        if existing:
            db_logger.warning("Relacionamento container-competição já existe", 
                             container_id=container_competition_dto.container_id,
                             competition_id=container_competition_dto.competition_id)
            return None
        
        container_competition = ContainerCompetition(
            container_id=container_competition_dto.container_id,
            competition_id=container_competition_dto.competition_id
        )
        db.add(container_competition)
        db.commit()
        db.refresh(container_competition)
        
        duration = time.time() - start_time
        db_logger.log_database("CREATE", "container_competitions", duration, 
                              container_id=container_competition.container_id,
                              competition_id=container_competition.competition_id)
        
        return ContainerCompetitionCreateDTO(
            container_id=container_competition.container_id,
            competition_id=container_competition.competition_id
        )
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao criar relacionamento container-competição", 
                       error=str(e),
                       container_id=container_competition_dto.container_id,
                       competition_id=container_competition_dto.competition_id,
                       duration_ms=round(duration * 1000, 2))
        raise e

def delete_container_competition(db: Session, container_id: str, competition_id: str) -> bool:
    """
    Deleta um relacionamento container-competição
    """
    start_time = time.time()
    db_logger.info("Iniciando deleção de relacionamento container-competição", 
                   container_id=container_id,
                   competition_id=competition_id)
    
    try:
        container_competition = db.query(ContainerCompetition).filter(
            ContainerCompetition.container_id == container_id,
            ContainerCompetition.competition_id == competition_id
        ).first()
        if not container_competition:
            db_logger.warning("Relacionamento container-competição não encontrado", 
                             container_id=container_id,
                             competition_id=competition_id)
            return False
        
        db.delete(container_competition)
        db.commit()
        
        duration = time.time() - start_time
        db_logger.log_database("DELETE", "container_competitions", duration, 
                              container_id=container_id,
                              competition_id=competition_id)
        
        return True
    
    except Exception as e:
        duration = time.time() - start_time
        db_logger.error("Erro ao deletar relacionamento container-competição", 
                       error=str(e),
                       container_id=container_id,
                       competition_id=competition_id,
                       duration_ms=round(duration * 1000, 2))
        raise e