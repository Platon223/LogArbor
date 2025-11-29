from marshmallow import ValidationError

def validate_db_data(data, schema):
    try:
        schema.load(data)
        return data
    except ValidationError as e:
        return f"error: {e}"