from marshmallow import Schema, fields, validate

class Services(Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    url = fields.String(required=True)
    alert_level = fields.String(required=True)
    user_id = fields.String(required=True)

services_schema = Services()