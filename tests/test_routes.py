import json
import pytest
from flask import Response
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def fake_post_comment_success(data):
    # Simulate a successful add/update of a comment.
    return Response(
        json.dumps({"message": "Comment added/updated successfully"}),
        status=201,
        mimetype="application/json",
    )


def fake_post_comment_bad_request(data):
    # Simulate a bad request due to missing fields.
    return Response(
        json.dumps({"error": "Missing required fields"}),
        status=400,
        mimetype="application/json",
    )


# Bypass the token_required decorator by patching it to return the function unmodified.
def bypass_token_required(func):
    return func


def test_root_route(client):
    response = client.get("/")
    assert response.status_code == 200


def test_add_comment_success(monkeypatch, client):
    # Patch the token_required decorator and post_comment function.
    monkeypatch.setattr("app.routes.stations.token_required", lambda f: f)
    monkeypatch.setattr("app.routes.stations.post_comment", fake_post_comment_success)

    payload = {
        "work_order_id": "WO0000001",
        "station_number": "2",
        "comment": "Waiting for parts",
    }
    response = client.post(
        "/comment", json=payload, headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "Comment added/updated successfully"


def test_add_comment_bad_request(monkeypatch, client):
    # Patch the token_required decorator and post_comment function.
    monkeypatch.setattr("app.routes.stations.token_required", lambda f: f)
    monkeypatch.setattr(
        "app.routes.stations.post_comment", fake_post_comment_bad_request
    )

    # Missing 'station_number' and 'comment'
    payload = {"work_order_id": "WO0000001"}
    response = client.post(
        "/comment", json=payload, headers={"Authorization": "Bearer valid_token"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
