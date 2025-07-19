from flask import Blueprint, request, jsonify
from app.models.user_model import create_user

users_bp = Blueprint("users", __name__)


@users_bp.post("/signup")
def add_user():
    data = request.get_json()
    create_user(data)
