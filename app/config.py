import os
from dotenv import load_dotenv

load_dotenv()

env = os.getenv("FLASK_ENV", "development")
if env == "development":
    load_dotenv(".env.development")
else:
    load_dotenv(".env.production")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    REGISTER_KEY = os.getenv("REGISTER_KEY")
