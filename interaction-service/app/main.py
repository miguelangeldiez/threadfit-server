from flask import Flask
from models import db
from routes import interaction_blueprint
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(interaction_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
