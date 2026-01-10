from marshmallow import Schema, fields, validate

class Alert(Schema):
    id = fields.String(required=True)
    message = fields.String(required=True)
    level = fields.String(required=True)
    time = fields.String(required=True)
    user_id = fields.String(required=True)
    service_id = fields.String(required=True)
    service_name = fields.String(required=True)
    viewed = fields.Boolean(required=True)

alerts_schema = Alert()