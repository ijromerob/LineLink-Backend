from app import create_app


def test_protected_route_without_token():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/protected-resource")  # replace with a real route
    assert response.status_code == 401
