# Importaciones estándar
import logging

# Importaciones de terceros
from flask import request
from flask_socketio import disconnect, emit
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
# Importaciones locales
from app import socketio
from models import User,db, Like, Post, Comment
from schemas import PostSchema, CommentSchema, UserSchema


# Configuración básica del logging para facilitar la depuración
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

post_schema = PostSchema()
comment_schema = CommentSchema()
user_schema = UserSchema()

def authenticate_socket():
    """
    Verifica la autenticidad del usuario mediante JWT.
    
    Retorna:
        user_id (int): ID del usuario autenticado.
        
    Lanza:
        Exception: Si el token no es válido o ha expirado.
    """
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        logger.info(f"Usuario autenticado: {user_id}")
        return user_id
    except Exception as e:
        logger.error(f"Error al verificar el token: {e}")
        emit('error', {'message': 'Token inválido o expirado'}, to=request.sid)
        disconnect()
        raise

@socketio.on('connect')
def handle_connect():
    """
    Maneja el evento de conexión de un cliente.
    
    Verifica la presencia y validez del token JWT proporcionado.
    Si el token es inválido o no se proporciona, desconecta al cliente.
    """
    logger.info(f"Cliente conectado: {request.sid}")
    token = request.args.get('token')
    if not token:
        logger.warning("No se proporcionó token")
        emit('error', {'message': 'Token no proporcionado'}, to=request.sid)
        disconnect()
        return
    try:
        user_id = authenticate_socket()
        logger.info(f"Usuario {user_id} conectado con éxito")
    except Exception:
        # La función authenticate_socket ya maneja el error y desconecta
        pass

@socketio.on('disconnect')
def handle_disconnect():
    """
    Maneja el evento de desconexión de un cliente.
    """
    logger.info(f"Cliente desconectado: {request.sid}")

@socketio.on('like_post')
def handle_like_post(data):
    """
    Maneja el evento de 'like_post' cuando un usuario da o quita un 'me gusta' a un post.

    Args:
        data (dict): Contiene 'post_id' del post a modificar.
    """
    logger.info(f"Evento recibido: like_post, Datos: {data}")
    
    # Autenticar al usuario
    try:
        user_id = authenticate_socket()
        if not user_id:
            logger.warning("Autenticación fallida")
            emit('error', {'message': 'Autenticación requerida'}, to=request.sid)
            return
    except Exception as e:
        logger.error(f"Error de autenticación: {e}")
        return

    # Validar que 'post_id' esté presente
    post_id = data.get('post_id')
    if not post_id:
        logger.warning("El ID del post es requerido")
        emit('error', {'message': 'El ID del post es requerido'}, to=request.sid)
        return

    try:
        # Usar un contexto de transacción
        with db.session.begin():
            # Consultar la publicación y bloquearla para evitar condiciones de carrera
            post = Post.query.with_for_update().get(post_id)
            if not post:
                logger.warning(f"El post con ID {post_id} no existe")
                emit('error', {'message': 'El post no existe'}, to=request.sid)
                return

            # Buscar si el usuario ya dio 'me gusta' a la publicación
            existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

            # Si el usuario ya dio 'me gusta', eliminarlo; si no, agregarlo
            if existing_like:
                db.session.delete(existing_like)
                post.likes_count = max(post.likes_count - 1, 0)  # Evitar valores negativos
                logger.info(f"Usuario {user_id} quitó 'me gusta' del post {post_id}")
            else:
                new_like = Like(user_id=user_id, post_id=post_id)
                db.session.add(new_like)
                post.likes_count += 1
                logger.info(f"Usuario {user_id} dio 'me gusta' al post {post_id}")

        # Serializar y emitir la actualización de likes
        serialized_post = post_schema.dump(post)
        emit('update_likes', serialized_post, broadcast=True, include_self=True)
        logger.info(f"Actualización de likes emitida para el post {post_id}")

    except IntegrityError:
        db.session.rollback()
        logger.error("El usuario ya ha dado 'me gusta' a este post")
        emit('error', {'message': 'Ya has dado "me gusta" a este post'}, to=request.sid)

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error de base de datos al procesar 'me gusta': {e}")
        emit('error', {'message': 'Error de base de datos al procesar "me gusta"'}, to=request.sid)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inesperado al procesar 'me gusta': {e}")
        emit('error', {'message': f'Error inesperado: {str(e)}'}, to=request.sid)


        

@socketio.on('comment_post')
def handle_comment_post(data):
    """
    Maneja el evento de 'comment_post' cuando un usuario comenta en un post.

    Args:
        data (dict): Contiene 'post_id' y 'content' del comentario.
    """
    logger.info(f"Evento recibido: comment_post, Datos: {data}")

    # Autenticar al usuario
    try:
        user_id = authenticate_socket()
        if not user_id:
            logger.warning("Autenticación fallida")
            emit('error', {'message': 'Autenticación requerida'}, to=request.sid)
            return
    except Exception as e:
        logger.error(f"Error de autenticación: {e}")
        return

    # Validar los datos de entrada
    post_id = data.get('post_id')
    content = data.get('content')

    if not post_id or not content:
        logger.warning("El ID del post y el contenido del comentario son requeridos")
        emit('error', {'message': 'El ID del post y el contenido son requeridos'}, to=request.sid)
        return

    if len(content.strip()) < 1 or len(content) > 500:
        logger.warning("El contenido del comentario no es válido")
        emit('error', {'message': 'El contenido del comentario debe tener entre 1 y 500 caracteres'}, to=request.sid)
        return

    try:
        # Usar un contexto de transacción para manejar los cambios en la base de datos
        with db.session.begin():
            post = Post.query.with_for_update().get(post_id)
            if not post:
                logger.warning(f"El post con ID {post_id} no existe")
                emit('error', {'message': 'El post no existe'}, to=request.sid)
                return

            # Crear un nuevo comentario
            new_comment = Comment(
                content=content.strip(),
                user_id=user_id,
                post_id=post.id
            )
            db.session.add(new_comment)

            # Actualizar el contador de comentarios en el post
            post.comments_count += 1
            db.session.add(post)

        # Serializar el comentario y emitirlo a los clientes conectados
        serialized_comment = comment_schema.dump(new_comment)
        emit('new_comment', serialized_comment, broadcast=True, include_self=True)
        logger.info(f"Nuevo comentario emitido para el post {post_id}")

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error de base de datos al procesar el comentario: {e}")
        emit('error', {'message': 'Error de base de datos al procesar el comentario'}, to=request.sid)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inesperado al procesar el comentario: {e}")
        emit('error', {'message': f'Error inesperado: {str(e)}'}, to=request.sid)

