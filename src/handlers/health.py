from src.utils.response import ok

def get(event, context):
    return ok({"status": "healthy"})
