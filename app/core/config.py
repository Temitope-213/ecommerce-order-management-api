import os

from dotenv import load_dotenv

load_dotenv()  # reads the .env file

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")