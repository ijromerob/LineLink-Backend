from functools import wraps
from flask import request, jsonify
import re


def validate_part_number(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json() or {}
        if "part_number" not in data:
            part_number = data.get("product_number")
        else:
            part_number = data["part_number"] or data["product_number"]

        if not part_number or not re.match(r"^\d{3}-\d{5}$", part_number):
            return jsonify({"error": "Invalid part_number format"}), 400
        return f(*args, **kwargs)

    return decorated


def validate_email(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json() or {}
        email = data["email"]
        if not email or not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            return jsonify({"error": "Invalid email format"}), 400
        return f(*args, **kwargs)

    return decorated


def validate_work_order_id(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        work_order_id = kwargs.get("work_order_id")
        if not work_order_id:
            data = request.get_json(silent=True) or {}
            work_order_id = data.get("work_order_id")

        if not work_order_id:
            return jsonify({"error": "Missing work_order_id parameter"}), 400

        if not work_order_id.startswith("WO") or not work_order_id[2:].isdigit():
            return jsonify({"error": "Invalid work_order_id format"}), 400

        return f(*args, **kwargs)

    return decorated


def validate_password(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json() or {}
        password = data["password"]
        if not password:
            return jsonify({"error": "Password is required"}), 400

        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400

        if not re.search(r"[A-Z]", password):
            return (
                jsonify(
                    {"error": "Password must contain at least one uppercase letter"}
                ),
                400,
            )

        if not re.search(r"[a-z]", password):
            return (
                jsonify(
                    {"error": "Password must contain at least one lowercase letter"}
                ),
                400,
            )

        if not re.search(r"\d", password):
            return jsonify({"error": "Password must contain at least one digit"}), 400

        if not re.search(r"[!@#$%^&*()_+=\-{}\[\]:;\"'<>,.?/\\|~`]", password):
            return (
                jsonify(
                    {"error": "Password must contain at least one special character"}
                ),
                400,
            )

        return f(*args, **kwargs)

    return decorated


def validate_company(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json() or {}
        company = data["company"]
        if not company or len(company) < 3:
            return jsonify({"error": "Company is required"}), 400

        return f(*args, **kwargs)

    return decorated
