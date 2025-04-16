from flask import Flask
from app.models import db
from app.config import Config
from app.extensions import socketio

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    socketio.init_app(app, cors_allowed_origins="*")
    socketio.run(app, host="0.0.0.0", port=5000,allow_unsafe_werkzeug=True)

