from flask import Flask
from .config import Config
from .models import db
from .routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    return app
