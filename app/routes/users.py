from flask import Blueprint, request
from app.models.user_model import create_user, log_in_user, patch_user_company

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


@users_bp.post("/signin")
def log_in():
    """
    Authenticate a user and return a JWT token
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
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              example: yourpassword
    responses:
      200:
        description: Successful login returns JWT token and user info
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            token:
              type: string
              description: JWT token for authentication
            user:
              type: object
              properties:
                user_id:
                  type: integer
                  example: 1
                account_type:
                  type: string
                  example: production_employee
                first_name:
                  type: string
                  example: Ivan
                last_name:
                  type: string
                  example: Romero
                company:
                  type: string
                  example: Acme Inc.
                email:
                  type: string
                  example: user@example.com
      401:
        description: Invalid email or password
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid email or password
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Internal server error
    """
    data = request.get_json()
    response = log_in_user(data)
    return response


@users_bp.patch("/<int:user_id>/company")
def change_company(user_id):
    """
    Update User's Company
    ---
    tags:
      - Users
    summary: Update the company of a specific user
    parameters:
      - in: path
        name: user_id
        required: true
        type: integer
        description: ID of the user to update
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - company
          properties:
            company:
              type: string
              example: "New Company Inc."
    responses:
      200:
        description: Company updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Company updated
      400:
        description: Invalid input
      404:
        description: User not found
      500:
        description: Server error
    """
    data = request.get_json()
    company = data["company"]
    response = patch_user_company(user_id, company)
    return response
