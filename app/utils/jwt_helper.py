import jwt
from flask import request, jsonify
from app.config import Config
from functools import wraps


def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("authToken")
        if not token:
            auth_header = request.headers.get("Authorization", None)
            if auth_header:
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    token = parts[1]
        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            data = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            request.user = data  # optional: set the user info in request for later use
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated
