from marshmallow import Schema, fields, validate

class JWT(Schema):
    id = fields.String(required=True)
    token = fields.String(required=True)
    user_id = fields.String(required=True)

jwt_schema = JWT()