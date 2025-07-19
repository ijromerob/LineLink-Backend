import os
import psycopg2
import bcrypt

# from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flasgger import Swagger

INSERT_NEW_USER = """
INSERT INTO Users (email, password_hash, account_type, first_name, last_name, company)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING user_id;
"""

# # reads the environment variables
# load_dotenv()

app = Flask(__name__)

swagger = Swagger(app)

database_url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(database_url)


# the routes that will be using
@app.post("/api/signup")
def create_user():
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


if __name__ == "__main__":
    app.run(debug=True)
