#main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import router
from database import init_db
from logger import setup_logging, get_structured_logger

# Configura logging global
logger = setup_logging()
app_logger = get_structured_logger("main")

app = FastAPI()
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.on_event("startup")
def on_startup():
    app_logger.info("Iniciando aplicação", service="lycosidae-interpreter")
    init_db()
    app_logger.info("Aplicação iniciada com sucesso", service="lycosidae-interpreter")

@app.get("/")
def read_root():
    response_data = {"message": "Microservice is up!", "service": "lycosidae-interpreter"}
    app_logger.log_api_response("/", 200, response_data)
    return response_data
