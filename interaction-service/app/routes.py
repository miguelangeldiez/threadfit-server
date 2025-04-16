import uuid
import logging

from flask import request
from flask_socketio import disconnect, emit
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .extensions import db, socketio
from .models import Post, Like, Comment
from .schemas import PostSchema, CommentSchema

logger = logging.getLogger(__name__)

post_schema = PostSchema()
comment_schema = CommentSchema()


# --------------------------- UTILS ---------------------------


def get_current_user():
    try:
        verify_jwt_in_request()
        return get_jwt_identity()
    except Exception as e:
        logger.error(f"JWT verification failed: {str(e)}")
        emit('error', {'message': 'Authentication failed'}, to=request.sid)
        disconnect()
        raise


def validate_uuid(id_value, field_name='ID'):
    try:
        return uuid.UUID(id_value, version=4)
    except Exception:
        emit('error', {'message': f'{field_name} inválido'}, to=request.sid)
        raise


# --------------------------- EVENTS ---------------------------


@socketio.on('connect')
def on_connect():
    logger.info(f"Client connected: {request.sid}")
    try:
        user_id = get_current_user()
        logger.info(f"User {user_id} authenticated successfully")
    except Exception:
        pass


@socketio.on('disconnect')
def on_disconnect():
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('like_post')
def on_like_post(data):
    logger.info(f"like_post event received: {data}")

    try:
        user_id = get_current_user()
        post_id = validate_uuid(data.get('post_id'), 'Post ID')
    except Exception:
        return

    try:
        with db.session.begin():
            post = Post.query.with_for_update().get(post_id)
            if not post:
                emit('error', {'message': 'Post not found'}, to=request.sid)
                return

            like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

            if like:
                db.session.delete(like)
                post.likes_count = max(post.likes_count - 1, 0)
                logger.info(f"User {user_id} removed like from post {post_id}")
            else:
                new_like = Like(user_id=user_id, post_id=post_id)
                db.session.add(new_like)
                post.likes_count += 1
                logger.info(f"User {user_id} liked post {post_id}")

        emit('update_likes', post_schema.dump(post), broadcast=True)

    except (IntegrityError, SQLAlchemyError) as e:
        db.session.rollback()
        logger.error(f"DB error on like_post: {str(e)}")
        emit('error', {'message': 'Database error processing like'}, to=request.sid)


@socketio.on('comment_post')
def on_comment_post(data):
    logger.info(f"comment_post event received: {data}")

    try:
        user_id = get_current_user()
        post_id = validate_uuid(data.get('post_id'), 'Post ID')
        content = data.get('content', '').strip()

        if not content or not (1 <= len(content) <= 500):
            emit('error', {'message': 'Content must be between 1 and 500 characters'}, to=request.sid)
            return

    except Exception:
        return

    try:
        with db.session.begin():
            post = Post.query.with_for_update().get(post_id)
            if not post:
                emit('error', {'message': 'Post not found'}, to=request.sid)
                return

            comment = Comment(content=content, user_id=user_id, post_id=post_id)
            db.session.add(comment)

            post.comments_count += 1

        emit('new_comment', comment_schema.dump(comment), broadcast=True)

    except (IntegrityError, SQLAlchemyError) as e:
        db.session.rollback()
        logger.error(f"DB error on comment_post: {str(e)}")
        emit('error', {'message': 'Database error processing comment'}, to=request.sid)
