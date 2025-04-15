from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity
)
from .models import User
from .schemas import UserCreateSchema, UserSignInSchema, UserSchema
from .extensions import db, limiter

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/sign-up', methods=['POST'])
@limiter.limit("5 per minute")
def sign_up():
    data = UserCreateSchema().load(request.get_json())

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "El correo ya está registrado"}), 400

    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Usuario registrado", "user": UserSchema().dump(new_user)}), 201

@auth.route('/sign-in', methods=['POST'])
@limiter.limit("10 per minute")
def sign_in():
    data = UserSignInSchema().load(request.get_json())

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Credenciales inválidas"}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserSchema().dump(user)
    ), 200

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify(access_token=new_access_token), 200
