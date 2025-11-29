from marshmallow import Schema, fields, validate

class Users(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=6))
    email = fields.String(required=True, validate=validate.Email())

users_schema = Users()