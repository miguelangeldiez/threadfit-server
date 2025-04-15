from flask import Blueprint, request, jsonify
from .models import db, User
from .schemas import UserSchema
from .utils import generate_token, decode_token
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)
user_schema = UserSchema()

@auth_bp.route("/sign-up", methods=["POST"])
def sign_up():
    data = request.get_json()
    errors = user_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "User already exists"}), 409

    user = User(username=data["username"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201

@auth_bp.route("/sign-in", methods=["POST"])
def sign_in():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username")).first()

    if not user or not user.check_password(data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user.id)
    return jsonify({"access_token": token}), 200

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    data = request.get_json()
    token = data.get("token")

    try:
        payload = decode_token(token)
        new_token = generate_token(payload["user_id"])
        return jsonify({"access_token": new_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401
