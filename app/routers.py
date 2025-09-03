# routers.py
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models import *
from schemas import *
from dbutils import get_user_by_email, get_user_by_username, create_user
from database import get_db
from typing import Optional

router = APIRouter(
    prefix="/route",
    tags=["route"]
)

###################################
##### Routers Functions Below #####
###################################

#Default function, change as needed
@router.get("")
async def root_func():
    return {"message": "Root function ran!"}
    
#Function for generic user creation based on a json DTO
#Input: UserCreateDTO
#Output: UserReadDTO
@router.post("/register", response_model=UserReadDTO, status_code=201)
async def user_register(payload: UserCreateDTO, db: Session = Depends(get_db)):
    try:
        if get_user_by_email(db, payload.email):
            raise HTTPException(400, detail="E-mail já cadastrado")
        if get_user_by_username(db, payload.username):
            raise HTTPException(400, detail="Username já cadastrado")
        
        user = create_user(db, payload)
        return user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))