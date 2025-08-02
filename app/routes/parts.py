from flask import Blueprint, request
from app.models.parts_model import get_all_products, get_needed_parts, add_part_request
from ..utils.jwt_helper import token_required

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


@parts_bp.post("/part_request")
def post_part_request():
    """
    Request Parts from Warehouse
    ---
    tags:
      - Parts
    summary: Supply parts to a station for a given work order
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - work_order_id
            - station_number
            - part_number
            - quantity_requested
            - requested_by
          properties:
            work_order_id:
              type: string
              example: "WO0000001"
              description: Work order ID in display format
            station_number:
              type: string
              example: "1"
              description: Station requesting the part
            part_number:
              type: string
              example: "200-00001"
              description: The part number being supplied
            quantity_requested:
              type: number
              example: 4
              description: Quantity of the part being requested
            requested_by:
              type: integer
              example: 2
              description: Person id requesting the part
    responses:
      201:
        description: Part supply logged successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Part requested successfully"
            supply_id:
              type: integer
              example: 12
      400:
        description: Bad request (e.g., missing or malformed fields)
        schema:
          type: object
          properties:
            error:
              type: string
              example: Missing or invalid input
      404:
        description: Work order or part not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Part or work order not found
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: Internal server error
    """
    data = request.get_json()
    response = add_part_request(data)
    return response
