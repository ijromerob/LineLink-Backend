from flask import Blueprint, request
from app.models.parts_model import get_all_products

parts_bp = Blueprint("parts", __name__)


@parts_bp.get("/products")
def get_products():
    """
    Get All Products
    ---
    tags:
      - Products
    summary: Retrieve all available products
    responses:
      200:
        description: List of all products
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  product_number:
                    type: string
                    example: "100-00001"
                  description:
                    type: string
                    example: "Compact Car"
      500:
        description: Server error
    """
    response = get_all_products()
    return response
