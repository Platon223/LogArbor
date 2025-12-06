from marshmallow import Schema, fields, validate

class Users(Schema):
    id = fields.String(required=True)
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=6))
    email = fields.String(required=True, validate=validate.Email())
    account_type = fields.String(required=True)
    remember = fields.Boolean(required=True)
    remember_expiration_date = fields.Date(required=True)

users_schema = Users()