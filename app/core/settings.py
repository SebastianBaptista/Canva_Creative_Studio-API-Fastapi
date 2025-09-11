from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG", "False") == "True"
    # Puedes agregar más variables según tus necesidades

settings = Settings()