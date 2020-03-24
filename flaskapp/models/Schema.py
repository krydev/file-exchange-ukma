from marshmallow import Schema, fields, validate, post_load

from flaskapp import guard
from flaskapp.models.Model import User


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(validate=validate.Length(min=8), required=True)

    @post_load
    def make_user(self, data, **kwargs):
        data['password'] = guard.hash_password(data['password'])
        return User(**data)


user_schema = UserSchema()