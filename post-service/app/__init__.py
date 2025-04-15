from flask import Flask
from .config import Config
from .extensions import db, jwt, limiter, cors
from .routes import posts


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})

    with app.app_context():
        db.create_all()

    # Registrar Blueprints
    app.register_blueprint(posts)

    return app
