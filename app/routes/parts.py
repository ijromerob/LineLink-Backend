from flask import Blueprint, request
from app.models.parts_model import get_all_products, get_needed_parts

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


@parts_bp.get("/needed_parts")
def get_parts_needed():
    """
    Get All Needed Parts
    ---
    tags:
      - Parts
    summary: Retrieve all parts needed for all work orders
    responses:
      200:
        description: Report generated successfully
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  work_order:
                    type: string
                    example: "WO0000001"
                  part_number:
                    type: string
                    example: "P-12345"
                  description:
                    type: string
                    example: "Widget Housing"
                  quantity_required:
                    type: integer
                    example: 100
                  quantity_supplied:
                    type: integer
                    example: 75
      500:
        description: Internal server error
    """
    response = get_needed_parts()
    return response
