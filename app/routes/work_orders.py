from flask import Blueprint, request
from app.models.work_order_model import (
    retrieve_work_orders,
    retrieve_units_by_work_order_id,
)

work_orders_bp = Blueprint("work_orders", __name__)


@work_orders_bp.get("/")
def obtain_work_orders():
    """
    Get all work orders with supply status
    ---
    tags:
      - Work Orders
    summary: Retrieve all work orders with supply and progress information
    description: Returns a list of work orders, showing how many parts are needed, how many have been supplied, and how many are still missing.
    produces:
      - application/json
    responses:
      200:
        description: A list of work orders
        schema:
          type: object
          properties:
            work_orders:
              type: array
              items:
                type: object
                properties:
                  work_order_id:
                    type: string
                    example: "WO0000001"
                  product_number:
                    type: string
                    example: "100-00001"
                  quantity_to_produce:
                    type: integer
                    example: 10
                  total_parts_needed:
                    type: integer
                    example: 4
                  parts_supplied:
                    type: integer
                    example: 2
                  parts_missing:
                    type: integer
                    example: 2
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
    """

    response = retrieve_work_orders()
    return response


@work_orders_bp.get("/<work_order_id>")
def get_work_order_by_id(work_order_id):
    """
    Get units and station statuses for a specific work order
    ---
    tags:
      - Work Orders
    summary: Retrieve units for a work order with station status and part info
    description: |
      Returns an array of units belonging to a specific work order.
      Each unit contains its associated stations, status (in progress, completed, etc.),
      and part requirements including quantities and descriptions.
    parameters:
      - name: work_order_id
        in: path
        required: true
        description: Work order ID in the format WOXXXXXXX (e.g., WO0000001)
        type: string
    responses:
      200:
        description: A list of units and their station progress
        schema:
          type: object
          properties:
            units:
              type: array
              items:
                type: object
                properties:
                  unit_number:
                    type: integer
                    example: 1
                  stations:
                    type: array
                    items:
                      type: object
                      properties:
                        station_number:
                          type: string
                          example: "1"
                        status:
                          type: string
                          enum:
                            - not_started
                            - in_progress
                            - completed
                            - alert
                            - hold
                          example: "in_progress"
                        part_number:
                          type: string
                          example: "200-00001"
                        part_description:
                          type: string
                          example: "Car Door"
                        quantity_required:
                          type: number
                          example: 4
                        quantity_supplied:
                          type: number
                          example: 2
      400:
        description: Invalid work order ID format
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid work order ID format"
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Database connection failed"
    """
    integer_work_order_id = int(work_order_id.replace("WO", ""))
    response = retrieve_units_by_work_order_id(integer_work_order_id)
    return response
