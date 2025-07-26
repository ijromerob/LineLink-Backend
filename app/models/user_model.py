import bcrypt
import jwt
from datetime import datetime, timedelta
from app.db import connection
from flask import jsonify
from app.config import Config

# query to insert a new user

INSERT_NEW_USER = """
INSERT INTO Users (email, password_hash, account_type, first_name, last_name, company)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING user_id;
"""


def create_user(data):

    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]
    company = data["company"]
    password = data["password"]

    # by default it will assign everything as production employee
    account_type = data.get("accountType", "production_employee")

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    INSERT_NEW_USER,
                    (
                        email,
                        password_hash,
                        account_type,
                        first_name,
                        last_name,
                        company,
                    ),
                )
                user_id = cursor.fetchone()[0]  # Get the returned user_id
        return (
            jsonify({"message": "User created successfully", "user_id": user_id}),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


LOGIN_USER = """
SELECT user_id, password_hash, account_type, first_name, last_name, company
FROM Users
WHERE email = %s;
"""


def log_in_user(data):
    email = data["email"]
    password = data["password"]

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    LOGIN_USER,
                    (email,),
                )
                user = cursor.fetchone()
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        user_id, stored_hash, account_type, first_name, last_name, company = user

        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):

            payload = {
                "user_id": user_id,
                "email": email,
                "account_type": account_type,
                "exp": datetime.utcnow() + timedelta(hours=4),
            }

            token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")

            return (
                jsonify(
                    {
                        "message": "Login successful",
                        "token": token,
                        "user": {
                            "user_id": user_id,
                            "account_type": account_type,
                            "first_name": first_name,
                            "last_name": last_name,
                            "company": company,
                            "email": email,
                        },
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


SELECT_USER_BY_EMAIL = """
SELECT user_id, account_type FROM Users WHERE email = %s
"""


def get_or_create_user(email, first_name, last_name):

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_USER_BY_EMAIL, (email,))
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            else:
                default_type = "production_employee"
                cursor.execute(
                    INSERT_NEW_USER,
                    (email, "-", default_type, first_name, last_name, "-"),
                )
                user_id = cursor.fetchone()[0]
                return user_id, default_type


UPDATE_USER_COMPANY = """
UPDATE users SET company = %s WHERE user_id = %s RETURNING user_id
"""


def patch_user_company(user_id, company):
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(UPDATE_USER_COMPANY, (company, user_id))
                result = cursor.fetchone()
                if not result:
                    return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "Company Updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
