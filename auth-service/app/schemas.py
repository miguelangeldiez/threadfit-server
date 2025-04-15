from marshmallow import fields, validate, Schema, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from .models import User

class UserCreateSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=64))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class UserSignInSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class BaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        load_instance = True
        include_fk = True

class UserSchema(BaseSchema):
    id = fields.UUID()
    username = auto_field()
    email = auto_field()

    class Meta(BaseSchema.Meta):
        model = User
        fields = ("id", "username", "email")
