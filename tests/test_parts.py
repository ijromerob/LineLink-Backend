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


# Fake responses for GET /products
def fake_get_all_products():
    data = [{"product_number": "100-00001", "description": "Compact Car"}]
    return Response(json.dumps(data), status=200, mimetype="application/json")


# Fake responses for GET /needed_parts
def fake_get_needed_parts():
    data = [
        {
            "work_order": "WO0000001",
            "part_number": "222-12345",
            "description": "Widget Housing",
            "quantity_required": 100,
            "quantity_supplied": 75,
        }
    ]
    return Response(json.dumps(data), status=200, mimetype="application/json")


# Fake response for POST /part_request
def fake_add_part_request(data):
    response_data = {"message": "Part requested successfully", "supply_id": 12}
    return Response(json.dumps(response_data), status=201, mimetype="application/json")


def test_get_products(monkeypatch, client):
    # Patch the get_all_products function from the parts model.
    monkeypatch.setattr(
        "app.models.parts_model.get_all_products", fake_get_all_products
    )
    response = client.get("/api/parts/products")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["product_number"] == "100-00001"


def test_get_needed_parts(monkeypatch, client):
    # Patch the get_needed_parts function from the parts model.
    monkeypatch.setattr(
        "app.models.parts_model.get_needed_parts", fake_get_needed_parts
    )
    response = client.get("/api/parts/needed_parts")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["part_number"] == "200-00001"
