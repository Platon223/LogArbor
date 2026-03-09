from marshmallow import Schema, fields, validate

class Services(Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    alert_level = fields.String(required=True)
    user_id = fields.String(required=True)
    log_retention = fields.Date(required=True, format="%Y-%m-%d")

services_schema = Services()