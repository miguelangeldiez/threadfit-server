from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from models import User

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
