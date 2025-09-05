from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import *
from schemas import *
from dbutils_mysql import *
from database import get_db
from typing import Optional
from logger import get_structured_logger
import time

router = APIRouter(
    prefix="/route",
    tags=["route"]
)

logger = get_structured_logger("routers")

def create_success_response(data, message="Operação realizada com sucesso", **kwargs):
    """Cria uma resposta de sucesso padronizada"""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": time.time(),
        **kwargs
    }

def create_error_response(message, error_code=None, details=None, **kwargs):
    """Cria uma resposta de erro padronizada"""
    return {
        "status": "error",
        "message": message,
        "error_code": error_code,
        "details": details,
        "timestamp": time.time(),
        **kwargs
    }

@router.get("")
async def root_func():
    """
    Função padrão, altere conforme necessário
    """
    start_time = time.time()
    logger.info("Acessando função raiz", endpoint="/route")
    
    response_data = {
        "message": "Root function ran!",
        "status": "success",
        "service": "lycosidae-interpreter",
        "timestamp": time.time(),
        "available_endpoints": {
            "users": "/route/register",
            "competitions": "/route/competitions",
            "exercises": "/route/exercises",
            "tags": "/route/tags",
            "teams": "/route/teams",
            "containers": "/route/containers",
            "relationships": "/route/user-competitions, /route/user-teams, etc."
        }
    }
    
    response_time = time.time() - start_time
    logger.log_api_response("/route", 200, response_data, response_time=response_time)
    
    return response_data
    
@router.post("/register", response_model=UserReadDTO, status_code=201)
async def user_register(payload: UserCreateDTO, db: Session = Depends(get_db)):
    """
    Função para criação genérica de usuário baseada em um DTO JSON
    Input: UserCreateDTO
    Output: UserReadDTO
    """
    start_time = time.time()
    logger.info("Iniciando registro de usuário", 
                email=payload.email, 
                username=payload.username,
                endpoint="/route/register")
    
    try:
        existing_email = get_user_by_email(db, payload.email)
        if existing_email:
            logger.warning("Tentativa de registro com email já cadastrado", email=payload.email)
            raise HTTPException(400, detail="E-mail já cadastrado")
        
        existing_username = get_user_by_username(db, payload.username)
        if existing_username:
            logger.warning("Tentativa de registro com username já cadastrado", username=payload.username)
            raise HTTPException(400, detail="Username já cadastrado")
        
        logger.info("Criando novo usuário", email=payload.email, username=payload.username)
        user = create_user(db, payload)
        
        response_time = time.time() - start_time
        logger.log_api_response("/route/register", 201, user.dict(), 
                               response_time=response_time,
                               user_id=user.id)
        
        return user
        
    except HTTPException as e:
        response_time = time.time() - start_time
        logger.error("Erro no registro de usuário", 
                    error=str(e.detail), 
                    status_code=e.status_code,
                    response_time=response_time)
        raise e
    except Exception as e:
        response_time = time.time() - start_time
        logger.error("Erro interno no registro de usuário", 
                    error=str(e), 
                    response_time=response_time)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/competitions", response_model=CompetitionReadDTO, status_code=201)
async def create_competition_endpoint(payload: CompetitionCreateDTO, db: Session = Depends(get_db)):
    """
    Cria uma nova competição
    """
    start_time = time.time()
    logger.info("Iniciando criação de competição", 
                name=payload.name,
                organizer=payload.organizer,
                invite_code=payload.invite_code,
                endpoint="/route/competitions")
    
    try:
        existing_competition = get_competition_by_invite_code(db, payload.invite_code)
        if existing_competition:
            logger.warning("Tentativa de criar competição com código de convite já existente", 
                          invite_code=payload.invite_code)
            raise HTTPException(400, detail="Código de convite já existe")
        
        logger.info("Criando nova competição", 
                   name=payload.name, 
                   organizer=payload.organizer)
        competition = create_competition(db, payload)
        
        response_time = time.time() - start_time
        logger.log_api_response("/route/competitions", 201, competition.dict(), 
                               response_time=response_time,
                               competition_id=competition.id)
        
        return competition
        
    except HTTPException as e:
        response_time = time.time() - start_time
        logger.error("Erro na criação de competição", 
                    error=str(e.detail), 
                    status_code=e.status_code,
                    response_time=response_time)
        raise e
    except Exception as e:
        response_time = time.time() - start_time
        logger.error("Erro interno na criação de competição", 
                    error=str(e), 
                    response_time=response_time)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/competitions/{competition_id}", response_model=CompetitionReadDTO)
async def get_competition_endpoint(competition_id: str, db: Session = Depends(get_db)):
    """
    Busca uma competição pelo ID
    """
    start_time = time.time()
    logger.info("Buscando competição por ID", 
                competition_id=competition_id,
                endpoint="/route/competitions/{competition_id}")
    
    try:
        competition = get_competition_by_id(db, competition_id)
        if not competition:
            logger.warning("Competição não encontrada", competition_id=competition_id)
            raise HTTPException(404, detail="Competição não encontrada")
        
        response_time = time.time() - start_time
        logger.log_api_response(f"/route/competitions/{competition_id}", 200, competition.dict(), 
                               response_time=response_time,
                               competition_id=competition.id)
        
        return competition
        
    except HTTPException as e:
        response_time = time.time() - start_time
        logger.error("Erro ao buscar competição", 
                    error=str(e.detail), 
                    status_code=e.status_code,
                    competition_id=competition_id,
                    response_time=response_time)
        raise e
    except Exception as e:
        response_time = time.time() - start_time
        logger.error("Erro interno ao buscar competição", 
                    error=str(e), 
                    competition_id=competition_id,
                    response_time=response_time)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/competitions/invite/{invite_code}", response_model=CompetitionReadDTO)
async def get_competition_by_invite_endpoint(invite_code: str, db: Session = Depends(get_db)):
    """
    Busca uma competição pelo código de convite
    """
    try:
        competition = get_competition_by_invite_code(db, invite_code)
        if not competition:
            raise HTTPException(404, detail="Competição não encontrada")
        
        return competition
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/competitions/{competition_id}")
async def update_competition_endpoint(competition_id: str, payload: CompetitionCreateDTO, db: Session = Depends(get_db)):
    """
    Atualiza uma competição existente
    """
    try:
        existing_competition = get_competition_by_id(db, competition_id)
        if not existing_competition:
            raise HTTPException(404, detail="Competição não encontrada")
        
        if payload.invite_code != existing_competition.invite_code:
            conflict_competition = get_competition_by_invite_code(db, payload.invite_code)
            if conflict_competition:
                raise HTTPException(400, detail="Código de convite já existe")
        
        competition = update_competition(db, competition_id, payload)
        if not competition:
            raise HTTPException(404, detail="Competição não encontrada")
        return competition.dict()
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/competitions/{competition_id}")
async def delete_competition_endpoint(competition_id: str, db: Session = Depends(get_db)):
    """
    Deleta uma competição
    """
    start_time = time.time()
    logger.info("Iniciando deleção de competição", 
                competition_id=competition_id,
                endpoint="/route/competitions/{competition_id}")
    
    try:
        success = delete_competition(db, competition_id)
        if not success:
            logger.warning("Tentativa de deletar competição inexistente", competition_id=competition_id)
            raise HTTPException(404, detail="Competição não encontrada")
        
        response_time = time.time() - start_time
        response_data = create_success_response(
            data={"competition_id": competition_id},
            message="Competição deletada com sucesso",
            operation="delete_competition"
        )
        
        logger.log_api_response(f"/route/competitions/{competition_id}", 200, response_data, 
                               response_time=response_time,
                               competition_id=competition_id)
        
        return response_data
        
    except HTTPException as e:
        response_time = time.time() - start_time
        logger.error("Erro ao deletar competição", 
                    error=str(e.detail), 
                    status_code=e.status_code,
                    competition_id=competition_id,
                    response_time=response_time)
        raise e
    except Exception as e:
        response_time = time.time() - start_time
        logger.error("Erro interno ao deletar competição", 
                    error=str(e), 
                    competition_id=competition_id,
                    response_time=response_time)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/exercises", response_model=ExerciseReadDTO, status_code=201)
async def create_exercise_endpoint(payload: ExerciseCreateDTO, db: Session = Depends(get_db)):
    """
    Cria um novo exercício
    """
    start_time = time.time()
    logger.info("Iniciando criação de exercício", 
                name=payload.name,
                difficulty=payload.difficulty,
                score=payload.score,
                endpoint="/route/exercises")
    
    try:
        exercise = create_exercise(db, payload)
        
        response_time = time.time() - start_time
        logger.log_api_response("/route/exercises", 201, exercise.dict(), 
                               response_time=response_time,
                               exercise_id=exercise.id)
        
        return exercise
        
    except Exception as e:
        response_time = time.time() - start_time
        logger.error("Erro interno na criação de exercício", 
                    error=str(e), 
                    response_time=response_time)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/exercises/{exercise_id}", response_model=ExerciseReadDTO)
async def get_exercise_endpoint(exercise_id: str, db: Session = Depends(get_db)):
    """
    Busca um exercício pelo ID
    """
    try:
        exercise = get_exercise_by_id(db, exercise_id)
        if not exercise:
            raise HTTPException(404, detail="Exercício não encontrado")
        
        return exercise
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/exercises/{exercise_id}", response_model=ExerciseReadDTO)
async def update_exercise_endpoint(exercise_id: str, payload: ExerciseCreateDTO, db: Session = Depends(get_db)):
    """
    Atualiza um exercício existente
    """
    try:
        exercise = update_exercise(db, exercise_id, payload)
        if not exercise:
            raise HTTPException(404, detail="Exercício não encontrado")
        
        return exercise
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/exercises/{exercise_id}")
async def delete_exercise_endpoint(exercise_id: str, db: Session = Depends(get_db)):
    """
    Deleta um exercício
    """
    start_time = time.time()
    logger.info("Iniciando deleção de exercício", 
                exercise_id=exercise_id,
                endpoint="/route/exercises/{exercise_id}")
    
    try:
        success = delete_exercise(db, exercise_id)
        if not success:
            logger.warning("Tentativa de deletar exercício inexistente", exercise_id=exercise_id)
            raise HTTPException(404, detail="Exercício não encontrado")
        
        response_time = time.time() - start_time
        response_data = create_success_response(
            data={"exercise_id": exercise_id},
            message="Exercício deletado com sucesso",
            operation="delete_exercise"
        )
        
        logger.log_api_response(f"/route/exercises/{exercise_id}", 200, response_data, 
                               response_time=response_time,
                               exercise_id=exercise_id)
        
        return response_data
        
    except HTTPException as e:
        response_time = time.time() - start_time
        logger.error("Erro ao deletar exercício", 
                    error=str(e.detail), 
                    status_code=e.status_code,
                    exercise_id=exercise_id,
                    response_time=response_time)
        raise e
    except Exception as e:
        response_time = time.time() - start_time
        logger.error("Erro interno ao deletar exercício", 
                    error=str(e), 
                    exercise_id=exercise_id,
                    response_time=response_time)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/tags", response_model=TagReadDTO, status_code=201)
async def create_tag_endpoint(payload: TagCreateDTO, db: Session = Depends(get_db)):
    """
    Cria uma nova tag
    """
    try:
        existing_tag = get_tag_by_type(db, payload.type)
        if existing_tag:
            raise HTTPException(400, detail="Tipo de tag já existe")
        
        tag = create_tag(db, payload)
        return tag
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags/{tag_id}", response_model=TagReadDTO)
async def get_tag_endpoint(tag_id: str, db: Session = Depends(get_db)):
    """
    Busca uma tag pelo ID
    """
    try:
        tag = get_tag_by_id(db, tag_id)
        if not tag:
            raise HTTPException(404, detail="Tag não encontrada")
        
        return tag
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags/type/{tag_type}", response_model=TagReadDTO)
async def get_tag_by_type_endpoint(tag_type: str, db: Session = Depends(get_db)):
    """
    Busca uma tag pelo tipo
    """
    try:
        tag = get_tag_by_type(db, tag_type)
        if not tag:
            raise HTTPException(404, detail="Tag não encontrada")
        
        return tag
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tags/{tag_id}", response_model=TagReadDTO)
async def update_tag_endpoint(tag_id: str, payload: TagCreateDTO, db: Session = Depends(get_db)):
    """
    Atualiza uma tag existente
    """
    try:
        existing_tag = get_tag_by_id(db, tag_id)
        if not existing_tag:
            raise HTTPException(404, detail="Tag não encontrada")
        
        if payload.type != existing_tag.type:
            conflict_tag = get_tag_by_type(db, payload.type)
            if conflict_tag:
                raise HTTPException(400, detail="Tipo de tag já existe")
        
        tag = update_tag(db, tag_id, payload)
        return tag
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tags/{tag_id}")
async def delete_tag_endpoint(tag_id: str, db: Session = Depends(get_db)):
    """
    Deleta uma tag
    """
    try:
        success = delete_tag(db, tag_id)
        if not success:
            raise HTTPException(404, detail="Tag não encontrada")
        
        return {"message": "Tag deletada com sucesso"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/teams", response_model=TeamReadDTO, status_code=201)
async def create_team_endpoint(payload: TeamCreateDTO, db: Session = Depends(get_db)):
    """
    Cria um novo time
    """
    try:
        competition = get_competition_by_id(db, payload.competition)
        if not competition:
            raise HTTPException(400, detail="Competição não encontrada")
        
        creator = get_user_by_id(db, payload.creator)
        if not creator:
            raise HTTPException(400, detail="Criador não encontrado")
        
        team = create_team(db, payload)
        return team
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teams/{team_id}", response_model=TeamReadDTO)
async def get_team_endpoint(team_id: str, db: Session = Depends(get_db)):
    """
    Busca um time pelo ID
    """
    try:
        team = get_team_by_id(db, team_id)
        if not team:
            raise HTTPException(404, detail="Time não encontrado")
        
        return team
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/teams/{team_id}", response_model=TeamReadDTO)
async def update_team_endpoint(team_id: str, payload: TeamCreateDTO, db: Session = Depends(get_db)):
    """
    Atualiza um time existente
    """
    try:
        competition = get_competition_by_id(db, payload.competition)
        if not competition:
            raise HTTPException(400, detail="Competição não encontrada")
        
        creator = get_user_by_id(db, payload.creator)
        if not creator:
            raise HTTPException(400, detail="Criador não encontrado")
        
        team = update_team(db, team_id, payload)
        if not team:
            raise HTTPException(404, detail="Time não encontrado")
        
        return team
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/teams/{team_id}")
async def delete_team_endpoint(team_id: str, db: Session = Depends(get_db)):
    """
    Deleta um time
    """
    try:
        success = delete_team(db, team_id)
        if not success:
            raise HTTPException(404, detail="Time não encontrado")
        
        return {"message": "Time deletado com sucesso"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/containers", status_code=201)
async def create_container_endpoint(payload: ContainerCreateDTO, db: Session = Depends(get_db)):
    """
    Cria um novo container
    """
    try:
        container = create_container(db, payload)
        return container.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/containers/{container_id}", response_model=ContainerReadDTO)
async def get_container_endpoint(container_id: str, db: Session = Depends(get_db)):
    """
    Busca um container pelo ID
    """
    try:
        container = get_container_by_id(db, container_id)
        if not container:
            raise HTTPException(404, detail="Container não encontrado")
        
        return container
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/containers/{container_id}", response_model=ContainerReadDTO)
async def update_container_endpoint(container_id: str, payload: ContainerCreateDTO, db: Session = Depends(get_db)):
    """
    Atualiza um container existente
    """
    try:
        container = update_container(db, container_id, payload)
        if not container:
            raise HTTPException(404, detail="Container não encontrado")
        
        return container
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/containers/{container_id}")
async def delete_container_endpoint(container_id: str, db: Session = Depends(get_db)):
    """
    Deleta um container
    """
    try:
        success = delete_container(db, container_id)
        if not success:
            raise HTTPException(404, detail="Container não encontrado")
        
        return {"message": "Container deletado com sucesso"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/user-competitions", response_model=UserCompetitionCreateDTO, status_code=201)
async def create_user_competition_endpoint(payload: UserCompetitionCreateDTO, db: Session = Depends(get_db)):
    """
    Cria um relacionamento usuário-competição
    """
    start_time = time.time()
    logger.info("Iniciando criação de relacionamento usuário-competição", 
                user_id=payload.user_id,
                competition_id=payload.competition_id,
                endpoint="/route/user-competitions")
    
    try:
        user = get_user_by_id(db, payload.user_id)
        if not user:
            logger.warning("Tentativa de criar relacionamento com usuário inexistente", 
                          user_id=payload.user_id)
            raise HTTPException(400, detail="Usuário não encontrado")
        
        competition = get_competition_by_id(db, payload.competition_id)
        if not competition:
            logger.warning("Tentativa de criar relacionamento com competição inexistente", 
                          competition_id=payload.competition_id)
            raise HTTPException(400, detail="Competição não encontrada")
        
        user_competition = create_user_competition(db, payload)
        if not user_competition:
            logger.warning("Tentativa de criar relacionamento já existente", 
                          user_id=payload.user_id,
                          competition_id=payload.competition_id)
            raise HTTPException(400, detail="Relacionamento já existe")
        
        response_time = time.time() - start_time
        logger.log_api_response("/route/user-competitions", 201, user_competition.dict(), 
                               response_time=response_time,
                               user_id=payload.user_id,
                               competition_id=payload.competition_id)
        
        return user_competition
        
    except HTTPException as e:
        response_time = time.time() - start_time
        logger.error("Erro na criação de relacionamento usuário-competição", 
                    error=str(e.detail), 
                    status_code=e.status_code,
                    user_id=payload.user_id,
                    competition_id=payload.competition_id,
                    response_time=response_time)
        raise e
    except Exception as e:
        response_time = time.time() - start_time
        logger.error("Erro interno na criação de relacionamento usuário-competição", 
                    error=str(e), 
                    user_id=payload.user_id,
                    competition_id=payload.competition_id,
                    response_time=response_time)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.delete("/user-competitions/{user_id}/{competition_id}")
async def delete_user_competition_endpoint(user_id: str, competition_id: str, db: Session = Depends(get_db)):
    """
    Deleta um relacionamento usuário-competição
    """
    start_time = time.time()
    logger.info("Iniciando deleção de relacionamento usuário-competição", 
                user_id=user_id,
                competition_id=competition_id,
                endpoint="/route/user-competitions/{user_id}/{competition_id}")
    
    try:
        success = delete_user_competition(db, user_id, competition_id)
        if not success:
            logger.warning("Tentativa de deletar relacionamento inexistente", 
                          user_id=user_id,
                          competition_id=competition_id)
            raise HTTPException(404, detail="Relacionamento não encontrado")
        
        response_time = time.time() - start_time
        response_data = create_success_response(
            data={"user_id": user_id, "competition_id": competition_id},
            message="Relacionamento usuário-competição deletado com sucesso",
            operation="delete_user_competition"
        )
        
        logger.log_api_response(f"/route/user-competitions/{user_id}/{competition_id}", 200, response_data, 
                               response_time=response_time,
                               user_id=user_id,
                               competition_id=competition_id)
        
        return response_data
        
    except HTTPException as e:
        response_time = time.time() - start_time
        logger.error("Erro ao deletar relacionamento usuário-competição", 
                    error=str(e.detail), 
                    status_code=e.status_code,
                    user_id=user_id,
                    competition_id=competition_id,
                    response_time=response_time)
        raise e
    except Exception as e:
        response_time = time.time() - start_time
        logger.error("Erro interno ao deletar relacionamento usuário-competição", 
                    error=str(e), 
                    user_id=user_id,
                    competition_id=competition_id,
                    response_time=response_time)
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/user-teams", response_model=UserTeamCreateDTO, status_code=201)
async def create_user_team_endpoint(payload: UserTeamCreateDTO, db: Session = Depends(get_db)):
    """
    Cria um relacionamento usuário-time
    """
    try:
        user = get_user_by_id(db, payload.user_id)
        if not user:
            raise HTTPException(400, detail="Usuário não encontrado")
        
        team = get_team_by_id(db, payload.team_id)
        if not team:
            raise HTTPException(400, detail="Time não encontrado")
        
        user_team = create_user_team(db, payload)
        if not user_team:
            raise HTTPException(400, detail="Relacionamento já existe")
        
        return user_team
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/user-teams/{user_id}/{team_id}")
async def delete_user_team_endpoint(user_id: str, team_id: str, db: Session = Depends(get_db)):
    """
    Deleta um relacionamento usuário-time
    """
    try:
        success = delete_user_team(db, user_id, team_id)
        if not success:
            raise HTTPException(404, detail="Relacionamento não encontrado")
        
        return {"message": "Relacionamento usuário-time deletado com sucesso"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/team-competitions", response_model=TeamCompetitionCreateDTO, status_code=201)
async def create_team_competition_endpoint(payload: TeamCompetitionCreateDTO, db: Session = Depends(get_db)):
    """
    Cria um relacionamento time-competição
    """
    try:
        team = get_team_by_id(db, payload.team_id)
        if not team:
            raise HTTPException(400, detail="Time não encontrado")
        
        competition = get_competition_by_id(db, payload.competition_id)
        if not competition:
            raise HTTPException(400, detail="Competição não encontrada")
        
        team_competition = create_team_competition(db, payload)
        if not team_competition:
            raise HTTPException(400, detail="Relacionamento já existe")
        
        return team_competition
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/team-competitions/{team_id}/{competition_id}")
async def delete_team_competition_endpoint(team_id: str, competition_id: str, db: Session = Depends(get_db)):
    """
    Deleta um relacionamento time-competição
    """
    try:
        success = delete_team_competition(db, team_id, competition_id)
        if not success:
            raise HTTPException(404, detail="Relacionamento não encontrado")
        
        return {"message": "Relacionamento time-competição deletado com sucesso"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exercise-tags", response_model=ExerciseTagCreateDTO, status_code=201)
async def create_exercise_tag_endpoint(payload: ExerciseTagCreateDTO, db: Session = Depends(get_db)):
    """
    Cria um relacionamento exercício-tag
    """
    try:
        exercise = get_exercise_by_id(db, payload.exercise_id)
        if not exercise:
            raise HTTPException(400, detail="Exercício não encontrado")
        
        tag = get_tag_by_id(db, payload.tag_id)
        if not tag:
            raise HTTPException(400, detail="Tag não encontrada")
        
        exercise_tag = create_exercise_tag(db, payload)
        if not exercise_tag:
            raise HTTPException(400, detail="Relacionamento já existe")
        
        return exercise_tag
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/exercise-tags/{exercise_id}/{tag_id}")
async def delete_exercise_tag_endpoint(exercise_id: str, tag_id: str, db: Session = Depends(get_db)):
    """
    Deleta um relacionamento exercício-tag
    """
    try:
        success = delete_exercise_tag(db, exercise_id, tag_id)
        if not success:
            raise HTTPException(404, detail="Relacionamento não encontrado")
        
        return {"message": "Relacionamento exercício-tag deletado com sucesso"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/exercise-competitions", response_model=ExerciseCompetitionCreateDTO, status_code=201)
async def create_exercise_competition_endpoint(payload: ExerciseCompetitionCreateDTO, db: Session = Depends(get_db)):
    """
    Cria um relacionamento exercício-competição
    """
    try:
        exercise = get_exercise_by_id(db, payload.exercise_id)
        if not exercise:
            raise HTTPException(400, detail="Exercício não encontrado")
        
        competition = get_competition_by_id(db, payload.competition_id)
        if not competition:
            raise HTTPException(400, detail="Competição não encontrada")
        
        exercise_competition = create_exercise_competition(db, payload)
        if not exercise_competition:
            raise HTTPException(400, detail="Relacionamento já existe")
        
        return exercise_competition
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/exercise-competitions/{exercise_id}/{competition_id}")
async def delete_exercise_competition_endpoint(exercise_id: str, competition_id: str, db: Session = Depends(get_db)):
    """
    Deleta um relacionamento exercício-competição
    """
    try:
        success = delete_exercise_competition(db, exercise_id, competition_id)
        if not success:
            raise HTTPException(404, detail="Relacionamento não encontrado")
        
        return {"message": "Relacionamento exercício-competição deletado com sucesso"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/container-competitions", response_model=ContainerCompetitionCreateDTO, status_code=201)
async def create_container_competition_endpoint(payload: ContainerCompetitionCreateDTO, db: Session = Depends(get_db)):
    """
    Cria um relacionamento container-competição
    """
    try:
        container = get_container_by_id(db, payload.container_id)
        if not container:
            raise HTTPException(400, detail="Container não encontrado")
        
        competition = get_competition_by_id(db, payload.competition_id)
        if not competition:
            raise HTTPException(400, detail="Competição não encontrada")
        
        container_competition = create_container_competition(db, payload)
        if not container_competition:
            raise HTTPException(400, detail="Relacionamento já existe")
        
        return container_competition
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/container-competitions/{container_id}/{competition_id}")
async def delete_container_competition_endpoint(container_id: str, competition_id: str, db: Session = Depends(get_db)):
    """
    Deleta um relacionamento container-competição
    """
    try:
        success = delete_container_competition(db, container_id, competition_id)
        if not success:
            raise HTTPException(404, detail="Relacionamento não encontrado")
        
        return {"message": "Relacionamento container-competição deletado com sucesso"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))