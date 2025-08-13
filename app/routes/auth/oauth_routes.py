import os
import requests
import jwt
from flask import Blueprint, redirect, request, jsonify, make_response
from urllib.parse import urlencode
from datetime import datetime, timedelta
from app.config import Config
from app.models.user_model import get_or_create_user

auth_bp = Blueprint("auth", __name__)


def get_redirect_uri():
    base_url = request.host_url.rstrip("/")
    return f"{base_url}/api/auth/callback"


# Get Google OAuth URLs
provider_cfg = requests.get(Config.GOOGLE_DISCOVERY_URL).json()
auth_endpoint = provider_cfg["authorization_endpoint"]
token_endpoint = provider_cfg["token_endpoint"]
userinfo_endpoint = provider_cfg["userinfo_endpoint"]


@auth_bp.route("/login")
def login():
    """
    Redirects user to Google OAuth2 authorization endpoint.
    ---
    tags:
      - Authentication
    summary: Start Google OAuth2 Login
    description: Redirects to Google for OAuth2 login with OpenID, email, and profile scopes.
    responses:
      302:
        description: Redirect to Google for authentication
    """
    params = {
        "client_id": Config.GOOGLE_CLIENT_ID,
        "redirect_uri": get_redirect_uri(),
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
    }
    return redirect(f"{auth_endpoint}?{urlencode(params)}")


@auth_bp.route("/callback")
def callback():
    """
    Handles Google's OAuth2 callback, retrieves user info, and returns a JWT.
    ---
    tags:
      - Authentication
    summary: Google OAuth2 callback
    description: |
      Accepts the authorization code from Google, exchanges it for an access token,
      retrieves user profile info, and returns a signed JWT for accessing the API.
    parameters:
      - name: code
        in: query
        required: true
        type: string
        description: Authorization code returned by Google after user login.
    responses:
      200:
        description: Successfully authenticated and returned JWT token
        schema:
          type: object
          properties:
            message:
              type: string
              example: Login successful
            token:
              type: string
              description: JWT token
            user:
              type: object
              properties:
                email:
                  type: string
                  example: user@example.com
                first_name:
                  type: string
                  example: Ivan
                last_name:
                  type: string
                  example: Romero
                account_type:
                  type: string
                  example: production_employee
      400:
        description: Error during OAuth2 callback or token exchange
    """
    code = request.args.get("code")

    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    # Exchange code for access token
    token_data = {
        "code": code,
        "client_id": Config.GOOGLE_CLIENT_ID,
        "client_secret": Config.GOOGLE_CLIENT_SECRET,
        "redirect_uri": get_redirect_uri(),
        "grant_type": "authorization_code",
    }
    token_response = requests.post(token_endpoint, data=token_data)
    if token_response.status_code != 200:
        return (
            jsonify(
                {"error": "failed to obtain token", "details": token_response.json()}
            ),
            400,
        )

    access_token = token_response.json()["access_token"]

    # Fetch user info
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        userinfo_response = requests.get(userinfo_endpoint, headers=headers, timeout=10)
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()
    except requests.exceptions.RequestException as e:
        print(f"[OAuth Callback] Failed to fetch user info: {e}")
        return (
            jsonify({"error": "Failed to retrieve user info", "details": str(e)}),
            400,
        )

    email = userinfo.get("email")
    first_name = userinfo.get("given_name")
    last_name = userinfo.get("family_name")

    if not all([email, first_name, last_name]):
        return jsonify({"error": "Incomplete user info received"}), 400

    user_id, account_type = get_or_create_user(email, first_name, last_name)

    payload = {
        "user_id": user_id,
        "email": email,
        "account_type": account_type,
        "exp": datetime.utcnow() + timedelta(hours=4),
    }

    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")
    response = make_response(redirect((f"{Config.FRONTEND_URL}/dashboard")))
    response.set_cookie(
        "authToken",
        token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=4 * 60 * 60,
        path="/",
    )
    return response
