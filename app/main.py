from fastapi import FastAPI
from app.api.v1.endpoints import user_endpoint  # importa tu router de usuarios
# Puedes importar más routers aquí

app = FastAPI(
    title="Canva API",
    version="1.0.0"
)

# Incluye los routers
app.include_router(user_endpoint.router)
# app.include_router(otro_router.router)  # para otros endpoints

# Si quieres crear las tablas automáticamente (opcional, solo si no existen)
# from app.db.session import engine
# from app.models.base import Base
# Base.metadata.create_all(bind=engine)

# Puedes agregar middlewares, CORS, eventos, etc. aquí

# Para ejecutar el servidor, usa el siguiente comando en la terminal:
# uvicorn app.main:app --reload
