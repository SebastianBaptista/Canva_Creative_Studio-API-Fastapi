import sys
from sqlalchemy import text

# Permitir importar 'app' como paquete
sys.path.insert(0, ".")

from app.db.session import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        
        print(result.fetchone())
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")
