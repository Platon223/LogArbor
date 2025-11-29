from marshmallow import Schema, fields, validate

class Users(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=6))
    email = fields.String(required=True, validate=validate.Email())
    account_type = fields.String(required=True)

users_schema = Users()