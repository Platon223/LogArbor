from marshmallow import Schema, fields, validate

class Verify_Codes(Schema):
    id = fields.String(required=True)
    code = fields.String(required=True)
    user_id = fields.String(required=True)
    expiration_date = fields.Date(required=True, format="%Y-%m-%d")

verify_codes_schema = Verify_Codes()