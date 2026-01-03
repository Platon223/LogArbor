from marshmallow import Schema, fields, validate

class Alert(Schema):
    id = fields.String(required=True)
    message = fields.String(required=True)
    level = fields.String(required=True)
    time = fields.String(required=True)

alerts_schema = Alert()