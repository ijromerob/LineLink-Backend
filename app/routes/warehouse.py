from flask import Blueprint, request
from app.models.warehouse_model import post_dispatch_parts
from ..utils.jwt_helper import token_required
from ..utils.validators import validate_work_order_id, validate_part_number

warehouse_bp = Blueprint("warehouse", __name__)


@warehouse_bp.post("/dispatch")
@token_required
@validate_work_order_id
@validate_part_number
def dispatch_parts():
    """
    Dispatch Parts from Warehouse
    ---
    security:
      - Bearer: []
    tags:
      - Warehouse
    summary: Log the dispatch of parts from the warehouse to a specific station for a work order
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
            - quantity_supplied
          properties:
            work_order_id:
              type: string
              example: "WO0000001"
              description: Work order ID in display format
            station_number:
              type: string
              example: "1"
              description: Station number receiving the parts
            part_number:
              type: string
              example: "200-00001"
              description: The part number being dispatched
            quantity_supplied:
              type: number
              example: 10
              description: Quantity of the part being supplied
    responses:
      201:
        description: Dispatch logged successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Part dispatch recorded successfully.
            supply_id:
              type: integer
              example: 101
      400:
        description: Invalid input or formatting
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid work_order_id format
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
    response = post_dispatch_parts(data)
    return response
