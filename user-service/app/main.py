from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_sqlalchemy import SQLAlchemy
from config import Config

# Inicialización de extensiones
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
db = SQLAlchemy()

jwt = JWTManager()
cors = CORS()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})
    limiter.init_app(app)

    # Registro único del blueprint de autenticación
    from routes import user
    app.register_blueprint(user)

    return app
