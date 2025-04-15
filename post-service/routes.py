import traceback
import uuid

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload

from app import db
from models import Comment, Post
from schemas import PostSchema, CommentSchema

posts = Blueprint('posts', __name__, url_prefix='/posts')

post_schema = PostSchema()
posts_schema = PostSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)


@posts.route('/all_posts', methods=['GET'])
@jwt_required()
def get_all_posts():
    try:
        current_user_id = get_jwt_identity()

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        pagination = (
            Post.query
            .options(
                joinedload(Post.user),          
                joinedload(Post.likes),         
                joinedload(Post.comments)      
            )
            .order_by(Post.timestamp.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        posts_with_relations = pagination.items
        posts_data = posts_schema.dump(posts_with_relations, context={'current_user_id': current_user_id})

        response = {
            "posts": posts_data,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page,
            "per_page": pagination.per_page,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            "error": "Error al obtener publicaciones",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500


@posts.route('/delete_post/<string:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    try:
        try:
            post_uuid = uuid.UUID(post_id, version=4)
        except ValueError:
            return jsonify({"msg": "ID de la publicación inválido. Debe ser un UUID válido."}), 400
        current_user_id_str = get_jwt_identity()
        if not current_user_id_str:
            return jsonify({"msg": "Usuario no autenticado."}), 401
        try:
            current_user_id = uuid.UUID(current_user_id_str, version=4)
        except ValueError:
            return jsonify({"msg": "ID de usuario inválido."}), 400
        post = Post.query.get(post_uuid)

        if not post:
            return jsonify({"msg": "Publicación no encontrada."}), 404
        if post.user_id != current_user_id:
            return jsonify({"msg": "No tienes permiso para realizar esta acción."}), 403

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


@posts.route('/create_post', methods=['POST'])
@jwt_required()
def create_post():
    try:
        user_id_str = get_jwt_identity()
        if not user_id_str:
            return jsonify({"msg": "Usuario no autenticado."}), 401
        try:
            user_id = uuid.UUID(user_id_str, version=4)
        except ValueError:
            return jsonify({"msg": "ID de usuario inválido."}), 400

        data = request.get_json()
        if not data:
            return jsonify({"msg": "No se proporcionaron datos."}), 400

        content = data.get('content')
        if not content:
            return jsonify({"msg": "El contenido de la publicación es requerido."}), 400

        new_post = Post(content=content, user_id=user_id, likes_count=0, comments_count=0)
        db.session.add(new_post)
        db.session.commit()

        post_data = post_schema.dump(new_post)
        return jsonify({
            "msg": "Publicación creada con éxito.",
            "post": post_data
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Error al crear la publicación",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500


@posts.route('/comments/<string:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    try:
        try:
            comment_uuid = uuid.UUID(comment_id, version=4)
        except ValueError:
            return jsonify({"msg": "ID del comentario inválido. Debe ser un UUID válido."}), 400

        current_user_id_str = get_jwt_identity()
        if not current_user_id_str:
            return jsonify({"msg": "Usuario no autenticado."}), 401
        try:
            current_user_id = uuid.UUID(current_user_id_str, version=4)
        except ValueError:
            return jsonify({"msg": "ID de usuario inválido."}), 400

        comment = Comment.query.get(comment_uuid)

        if not comment:
            return jsonify({"msg": "Comentario no encontrado."}), 404

        if comment.user_id != current_user_id:
            return jsonify({"msg": "No tienes permiso para realizar esta acción."}), 403

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


@posts.route('/<string:post_id>/comments', methods=['GET'])
@jwt_required()
def get_comments(post_id):
    try:
        try:
            post_uuid = uuid.UUID(post_id, version=4)
        except ValueError:
            return jsonify({"error": "ID de la publicación inválido. Debe ser un UUID válido."}), 400

        post = Post.query.options(joinedload(Post.comments)).get(post_uuid)

        if not post:
            return jsonify({"error": "Publicación no encontrada"}), 404

        comments = post.comments 
        comments_data = comments_schema.dump(comments)

        return jsonify(comments_data), 200

    except Exception as e:
        return jsonify({
            "error": "Error al obtener comentarios",
            "message": str(e),
            "trace": traceback.format_exc()
        }), 500
