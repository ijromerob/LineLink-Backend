from flask import Blueprint, request
from app.models.user_model import create_user

users_bp = Blueprint("users", __name__)


@users_bp.post("/signup")
def add_user():
    """
    Create a new user account
    ---
    tags:
      - Users
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - firstName
            - lastName
            - email
            - company
            - password
          properties:
            firstName:
              type: string
            lastName:
              type: string
            email:
              type: string
            company:
              type: string
            password:
              type: string
            accountType:
              type: string
              default: production_employee
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            user_id:
              type: integer
              example: 1
      500:
        description: Server error
    """
    data = request.get_json()
    response = create_user(data)
    return response
