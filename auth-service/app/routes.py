from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from app import db, limiter
from models import User
from schemas import UserSchema

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/sign-up', methods=['POST'])
@limiter.limit("5 per minute")
def sign_up():
    data = request.get_json()
    username = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"msg": "Todos los campos son obligatorios"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "El correo ya está registrado."}), 400

    new_user = User(username=username, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "Usuario registrado con éxito","user": UserSchema().dump(new_user)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al registrar usuario."}), 500



@auth.route('/sign-in', methods=['POST'])
@limiter.limit("10 per minute")
def sign_in():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "Usuario no encontrado."}), 404

    if not user.check_password(password):
        return jsonify({"msg": "Credenciales incorrectas."}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    user_data = UserSchema().dump(user)

    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data
    ), 200

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify(access_token=new_access_token), 200
