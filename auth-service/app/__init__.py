from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .routes import auth_bp
from flask_cors import CORS
from flask_jwt_extended import JWTManager

db = SQLAlchemy()  # Declarado aquí

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Importar modelos dentro del contexto para evitar problemas
    from . import models  

    with app.app_context():
        db.create_all()

    CORS(app)
    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    return app
