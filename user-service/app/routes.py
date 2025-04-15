# -------------------------------------------------------------------
# IMPORTACIONES
# -------------------------------------------------------------------

# Importaciones estándar
# (En este caso, no se utilizan librerías estándar de Python)

# Importaciones de terceros
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Importaciones locales
from .models import User, Post
from .schemas import UserSchema

# -------------------------------------------------------------------
# CONFIGURACIÓN DEL BLUEPRINT
# -------------------------------------------------------------------

user= Blueprint('user', __name__, url_prefix='/user')

# -------------------------------------------------------------------
# RUTAS DEL BLUEPRINT 'user'
# -------------------------------------------------------------------

@user.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """
    Ruta para obtener el perfil del usuario autenticado.
    
    Método: GET
    Autenticación: Requerida (JWT)
    
    Retorna:
        - 200: Datos del usuario (id, username, email).
        - 404: Si el usuario no se encuentra.
    """
    # Obtener el ID del usuario desde el token JWT
    user_id = get_jwt_identity()
    
    # Consultar el usuario en la base de datos
    user = User.query.get(user_id)
    
    if not user:
        # Si el usuario no existe, retornar un error 404
        return jsonify({"msg": "Usuario no encontrado."}), 404
    
    # Retornar los datos del usuario en formato JSON
    return jsonify(UserSchema().dump(user)), 200


@user.route('/<string:user_id>/posts', methods=['GET'])
@jwt_required()
def get_user_posts(user_id):
    """
    Ruta para obtener los posts de un usuario específico.
    
    Método: GET
    Autenticación: Requerida (JWT)
    
    Parámetros de URL:
        - user_id (string): ID del usuario cuyos posts se desean obtener.
    
    Parámetros de Consulta (Opcionales):
        - page (int): Número de página para la paginación (por defecto: 1).
        - per_page (int): Número de posts por página (por defecto: 10).
    
    Retorna:
        - 200: Lista de posts del usuario con información adicional.
        - 403: Si el usuario autenticado intenta acceder a los posts de otro usuario.
    """
    # Obtener el ID del usuario autenticado desde el token JWT
    current_user_id = get_jwt_identity()

    # Verificar que el usuario autenticado está solicitando sus propios posts
    if current_user_id != user_id:
        return jsonify({"msg": "Acceso no autorizado"}), 403

    # Obtener parámetros de paginación de la consulta
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Consultar los posts del usuario con paginación
    posts_pagination = Post.query.filter_by(user_id=user_id)\
        .order_by(Post.timestamp.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    # Serializar los datos de los posts
    user_posts_data = [
        {
            "id": post.id,
            "content": post.content,
            "timestamp": post.timestamp.isoformat(),
            "likes_count": post.likes_count,
            "comments_count": post.comments_count
        } 
        for post in posts_pagination.items
    ]

    # Retornar los datos de los posts junto con la información de paginación
    return jsonify({
        "posts": user_posts_data,
        "total": posts_pagination.total,
        "pages": posts_pagination.pages,
        "current_page": posts_pagination.page
    }), 200
