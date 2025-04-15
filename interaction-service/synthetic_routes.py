from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Post, Comment, Like
from app import db
from faker import Faker
import random

# Crear instancia de Faker
faker = Faker()

# Crear Blueprint
synthetic_bp = Blueprint('synthetic', __name__)

# Ruta para generar usuarios sintéticos (PROTEGIDA)
@synthetic_bp.route('/users', methods=['POST'])
@jwt_required()
def generate_users():
    count = int(request.json.get('count', 10))  # Cantidad de usuarios a generar (por defecto 10)
    users = []

    for _ in range(count):
        user = User(
            username=faker.user_name(),
            email=faker.email(),
            password_hash="synthetic_password_hash"
        )
        users.append(user)
        db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": f"Se generaron {count} usuarios sintéticos.",
        "users": [{"id": str(user.id), "username": user.username, "email": user.email} for user in users]
    }), 201

# Ruta para generar posts sintéticos (PROTEGIDA)
@synthetic_bp.route('/posts', methods=['POST'])
@jwt_required()
def generate_posts():
    user_id = request.json.get('user_id')  # ID del usuario para asociar posts
    count = int(request.json.get('count', 5))  # Cantidad de posts a generar (por defecto 5)

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    posts = []
    for _ in range(count):
        post = Post(
            content=faker.text(max_nb_chars=200),
            user_id=user.id,
            likes_count=0,
            comments_count=0
        )
        posts.append(post)
        db.session.add(post)
    db.session.commit()

    return jsonify({
        "message": f"Se generaron {count} posts sintéticos para el usuario {user.username}.",
        "posts": [{"id": str(post.id), "content": post.content} for post in posts]
    }), 201

# Ruta para generar comentarios sintéticos (PROTEGIDA)
@synthetic_bp.route('/comments', methods=['POST'])
@jwt_required()
def generate_comments():
    post_id = request.json.get('post_id')  # ID del post para asociar comentarios
    count = int(request.json.get('count', 3))  # Cantidad de comentarios a generar (por defecto 3)

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post no encontrado"}), 404

    comments = []
    for _ in range(count):
        user = random.choice(User.query.all())
        comment = Comment(
            content=faker.text(max_nb_chars=100),
            user_id=user.id,
            post_id=post.id
        )
        comments.append(comment)
        db.session.add(comment)
    db.session.commit()

    return jsonify({
        "message": f"Se generaron {count} comentarios sintéticos para el post {post.id}.",
        "comments": [{"id": str(comment.id), "content": comment.content} for comment in comments]
    }), 201

@synthetic_bp.route('/likes', methods=['POST'])
@jwt_required()
def generate_likes():
    post_id = request.json.get('post_id')  # ID del post para asociar likes
    count = int(request.json.get('count', 5))  # Cantidad de likes a generar (por defecto 5)

    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post no encontrado"}), 404

    existing_user_ids = {like.user_id for like in post.likes}
    all_user_ids = {user.id for user in User.query.all()}
    available_user_ids = list(all_user_ids - existing_user_ids)

    if not available_user_ids:
        return jsonify({"error": "No hay más usuarios disponibles para dar likes en este post."}), 400

    likes_to_create = min(count, len(available_user_ids))
    selected_user_ids = random.sample(available_user_ids, likes_to_create)

    likes = []
    for user_id in selected_user_ids:
        like = Like(
            user_id=user_id,
            post_id=post.id
        )
        likes.append(like)
        db.session.add(like)

    # Actualizar el contador de likes
    post.likes_count += len(likes)
    db.session.add(post)  # Asegurarse de añadir el post a la sesión si no está ya incluido

    db.session.commit()

    return jsonify({
        "message": f"Se generaron {len(likes)} likes sintéticos para el post {post.id}.",
        "likes": [{"id": str(like.id), "user_id": str(like.user_id)} for like in likes]
    }), 201
