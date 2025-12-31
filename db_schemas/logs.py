from marshmallow import Schema, fields, validate

class Logs(Schema):
    id = fields.String(required=True)
    service_id = fields.String(required=True)
    message = fields.String(required=True)
    level = fields.String(required=True)
    time = fields.String(required=True)

logs_schema = Logs()