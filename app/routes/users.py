from flask import Blueprint, request, jsonify
from app.models.user_model import create_user

users_bp = Blueprint("users", __name__)


@users_bp.get("/")
def get_users():
    try:
        user_id = "1"
        return jsonify({"user_id": user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
