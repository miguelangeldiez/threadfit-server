from app import create_app
from flask_cors import CORS
from flask_jwt_extended import JWTManager

app = create_app()
CORS(app)
jwt = JWTManager(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
