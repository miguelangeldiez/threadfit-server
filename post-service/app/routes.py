import traceback
import uuid

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload

from .extensions import db
from .models import Comment, Post
from .schemas import PostSchema, CommentSchema

posts = Blueprint('posts', __name__, url_prefix='/posts')

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


def validate_uuid(id_str, name="ID"):
    try:
        return uuid.UUID(id_str, version=4)
    except ValueError:
        response = {"msg": f"{name} inválido. Debe ser un UUID válido."}
        return jsonify(response), 400


@posts.route('/all_posts', methods=['GET'])
@jwt_required()
def get_all_posts():
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = (
            Post.query.options(
                joinedload(Post.user),
                joinedload(Post.likes),
                joinedload(Post.comments)
            )
            .order_by(Post.timestamp.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        posts_data = PostSchema(many=True, context={'current_user_id': current_user_id}).dump(pagination.items)

        return jsonify({
            "posts": posts_data,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "per_page": pagination.per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Error al obtener publicaciones",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500


@posts.route('/create_post', methods=['POST'])
@jwt_required()
def create_post():
    try:
        user_id_str = get_jwt_identity()
        user_id = uuid.UUID(user_id_str, version=4)

        data = request.get_json()
        content = data.get('content') if data else None

        if not content:
            return jsonify({"msg": "El contenido de la publicación es requerido."}), 400

        new_post = Post(content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        return jsonify({
            "msg": "Publicación creada con éxito.",
            "post": post_schema.dump(new_post)
        }), 201

    except (ValueError, AttributeError):
        return jsonify({"msg": "ID de usuario inválido."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Error al crear la publicación",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500


@posts.route('/delete_post/<string:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    post_uuid_or_resp = validate_uuid(post_id, "ID de la publicación")
    if isinstance(post_uuid_or_resp, tuple):
        return post_uuid_or_resp

    current_user_id = uuid.UUID(get_jwt_identity(), version=4)

    post = Post.query.get(post_uuid_or_resp)

    if not post:
        return jsonify({"msg": "Publicación no encontrada."}), 404

    if post.user_id != current_user_id:
        return jsonify({"msg": "No tienes permiso para realizar esta acción."}), 403

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"msg": "Publicación eliminada con éxito."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Error al eliminar la publicación",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500


@posts.route('/<string:post_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(post_id):
    post_uuid_or_resp = validate_uuid(post_id, "ID de la publicación")
    if isinstance(post_uuid_or_resp, tuple):
        return post_uuid_or_resp

    post = Post.query.options(joinedload(Post.comments)).get(post_uuid_or_resp)

    if not post:
        return jsonify({"error": "Publicación no encontrada"}), 404

    return jsonify(comments_schema.dump(post.comments)), 200


@posts.route('/comments/<string:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    comment_uuid_or_resp = validate_uuid(comment_id, "ID del comentario")
    if isinstance(comment_uuid_or_resp, tuple):
        return comment_uuid_or_resp

    current_user_id = uuid.UUID(get_jwt_identity(), version=4)

    comment = Comment.query.get(comment_uuid_or_resp)

    if not comment:
        return jsonify({"msg": "Comentario no encontrado."}), 404

    if comment.user_id != current_user_id:
        return jsonify({"msg": "No tienes permiso para realizar esta acción."}), 403

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({"msg": "Comentario eliminado con éxito."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Error al eliminar el comentario",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500
