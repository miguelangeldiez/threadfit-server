# -------------------------------------------------------------------
# IMPORTACIONES
# -------------------------------------------------------------------

# Importaciones de terceros
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

# Importaciones locales
from .models import User, Post, Comment, Like

# -------------------------------------------------------------------
# ESQUEMAS DE SERIALIZACIÓN CON MARSHMALLOW
# -------------------------------------------------------------------

class BaseSchema(SQLAlchemyAutoSchema):
    """
    Esquema base que define opciones comunes para otros esquemas.
    """
    class Meta:
        load_instance = True  # Permite cargar instancias de SQLAlchemy directamente
        include_relationships = True  # Incluye relaciones definidas en los modelos
        include_fk = True  # Incluye claves foráneas

class UserSchema(BaseSchema):
    id = fields.UUID()
    username = auto_field()
    email = auto_field()

    class Meta(BaseSchema.Meta):
        model = User
        fields = ("id", "username", "email")

class LikeSchema(BaseSchema):
    """
    Esquema para serializar y deserializar objetos Like.
    Incluye los campos 'id', 'post_id' y 'user_id'.
    """
    id = fields.UUID()
    post_id = fields.UUID()
    user_id = fields.UUID()

    class Meta(BaseSchema.Meta):
        model = Like
        fields = ("id", "post_id", "user_id")

class CommentSchema(BaseSchema):
    """
    Esquema para serializar y deserializar objetos Comment.
    Incluye los campos 'id', 'content', 'timestamp', 'user' y 'post_id'.
    """
    id = fields.UUID()
    content = auto_field()
    timestamp = auto_field()
    post_id = fields.UUID()
    user = fields.Nested(UserSchema)

    class Meta(BaseSchema.Meta):
        model = Comment
        fields = ("id", "content", "timestamp", "user", "post_id")

class PostSchema(BaseSchema):
    """
    Esquema para serializar y deserializar objetos Post.
    Incluye los campos 'id', 'content', 'timestamp', 'user', 'likes_count', 'comments_count' y 'comments'.
    """
    id = fields.UUID()
    content = auto_field()
    timestamp = auto_field()
    user = fields.Nested(UserSchema)
    likes_count = fields.Method("get_likes_count")
    comments_count = fields.Method("get_comments_count")
    comments = fields.Nested(CommentSchema, many=True)

    class Meta(BaseSchema.Meta):
        model = Post
        fields = ("id", "content", "timestamp", "user", "likes_count", "comments_count", "comments")

    def get_likes_count(self, obj):
        """
        Método personalizado para obtener el número de 'likes' de un post.

        Args:
            obj (Post): Instancia del modelo Post.

        Returns:
            int: Número de 'likes' del post.
        """
        return obj.likes_count

    def get_comments_count(self, obj):
        """
        Método personalizado para obtener el número de comentarios de un post.

        Args:
            obj (Post): Instancia del modelo Post.

        Returns:
            int: Número de comentarios del post.
        """
        return obj.comments_count

# -------------------------------------------------------------------
# FIN DE LOS ESQUEMAS
# -------------------------------------------------------------------
