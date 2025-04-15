from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from .models import User, Post, Comment


class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        load_instance = True
        include_relationships = True
        include_fk = True


class UserSchema(BaseSchema):
    id = fields.UUID()
    username = auto_field()
    email = auto_field()

    class Meta(BaseSchema.Meta):
        model = User
        fields = ("id", "username", "email")


class CommentSchema(BaseSchema):
    id = fields.UUID()
    content = auto_field()
    timestamp = auto_field()
    post_id = fields.UUID()
    user = fields.Nested(UserSchema)

    class Meta(BaseSchema.Meta):
        model = Comment
        fields = ("id", "content", "timestamp", "user", "post_id")


class PostSchema(BaseSchema):
    id = fields.UUID()
    content = auto_field()
    timestamp = auto_field()
    user = fields.Nested(UserSchema)
    likes_count = fields.Method("get_likes_count")
    comments_count = fields.Method("get_comments_count")
    comments = fields.Nested(CommentSchema, many=True)

    class Meta(BaseSchema.Meta):
        model = Post
        fields = (
            "id",
            "content",
            "timestamp",
            "user",
            "likes_count",
            "comments_count",
            "comments"
        )

    def get_likes_count(self, obj):
        return obj.likes_count or 0

    def get_comments_count(self, obj):
        return obj.comments_count or 0
