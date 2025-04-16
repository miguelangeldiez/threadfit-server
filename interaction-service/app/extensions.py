from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
cors = CORS()
socketio = SocketIO(cors_allowed_origins="*")