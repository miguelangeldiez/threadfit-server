# Importaciones de terceros
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID
# Importaciones locales
from app import db


# -------------------------------------------------------------------
# MODELOS DE LA BASE DE DATOS
# -------------------------------------------------------------------

class User(db.Model):
    """
    Modelo que representa a un usuario en la plataforma.
    """
    __tablename__ = 'users'

    # Columnas de la tabla 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    # Relaciones con otros modelos
    posts = db.relationship('Post', back_populates='user', cascade="all, delete-orphan")
    comments = db.relationship('Comment', back_populates='user', cascade="all, delete-orphan")
    likes = db.relationship('Like', back_populates='user', cascade="all, delete-orphan")

    # -------------------------------------------------------------------
    # MÉTODOS DE INSTANCIA
    # -------------------------------------------------------------------

    def set_password(self, password):
        """
        Genera un hash de la contraseña y lo almacena.

        Args:
            password (str): Contraseña en texto plano.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifica si la contraseña proporcionada coincide con el hash almacenado.

        Args:
            password (str): Contraseña en texto plano a verificar.

        Returns:
            bool: True si la contraseña es válida, False de lo contrario.
        """
        return check_password_hash(self.password_hash, password)

    def has_liked_post(self, post_id):
        """
        Verifica si el usuario ha dado 'me gusta' a un post específico.

        Args:
            post_id (int): ID del post a verificar.

        Returns:
            bool: True si el usuario ha dado 'me gusta', False de lo contrario.
        """
        return Like.query.filter_by(user_id=self.id, post_id=post_id).first() is not None

    def __repr__(self):
        """
        Representación en cadena del objeto User.

        Returns:
            str: Representación del usuario.
        """
        return f"<User {self.username}>"



class Post(db.Model):
    """
    Modelo que representa una publicación en la plataforma.
    """
    __tablename__ = 'posts'
    
    # Columnas de la tabla 'posts'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)

    def check_liked_by_user(self, obj):
        current_user_id = self.context.get('current_user_id')
        if not current_user_id:
            return False
        return any(like.user_id == current_user_id for like in obj.likes)

    # Relaciones con otros modelos
    user = db.relationship('User', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade="all, delete-orphan")
    likes = db.relationship('Like', back_populates='post', cascade="all, delete-orphan")

    def __repr__(self):
        """
        Representación en cadena del objeto Post.

        Returns:
            str: Representación del post.
        """
        return f"<Post {self.id} by {self.user.username}>"


class Comment(db.Model):
    """
    Modelo que representa un comentario en una publicación.
    """
    __tablename__ = 'comments'
    
    # Columnas de la tabla 'comments'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False) 
    post_id = db.Column(UUID(as_uuid=True), db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)

    # Relaciones con otros modelos
    user = db.relationship('User', back_populates='comments')
    post = db.relationship('Post', back_populates='comments')

    def __repr__(self):
        """
        Representación en cadena del objeto Comment.

        Returns:
            str: Representación del comentario.
        """
        return f"<Comment {self.id} by {self.user.username} on Post {self.post.id}>"


class Like(db.Model):
    """
    Modelo que representa un 'me gusta' en una publicación.
    """
    __tablename__ = 'likes'

    # Columnas de la tabla 'likes'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)  
    post_id = db.Column(UUID(as_uuid=True), db.ForeignKey('posts.id', ondelete="CASCADE"), nullable=False)  

    # Relaciones con otros modelos
    user = db.relationship('User', back_populates='likes')
    post = db.relationship('Post', back_populates='likes')

    # Restricciones de la tabla
    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name='_user_post_uc'),
    )

    def __repr__(self):
        """
        Representación en cadena del objeto Like.

        Returns:
            str: Representación del 'me gusta'.
        """
        return f"<Like by {self.user.username} on Post {self.post.id}>"

# -------------------------------------------------------------------
# FIN DE LOS MODELOS
# -------------------------------------------------------------------
