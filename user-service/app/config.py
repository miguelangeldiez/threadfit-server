import os
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'super_secret_key')
    SQLALCHEMY_DATABASE_URI = make_url(os.environ.get('DATABASE_URL')).set(drivername='postgresql+psycopg')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    JWT_TOKEN_LOCATION = ['headers', 'query_string']
    JWT_QUERY_STRING_NAME = 'token'

    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
