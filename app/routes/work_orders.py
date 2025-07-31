from flask import Blueprint, request
from app.models.work_order_model import (
    retrieve_work_orders,
    retrieve_units_by_work_order_id,
    add_work_order,
    post_completion,
)

work_orders_bp = Blueprint("work_orders", __name__)


@work_orders_bp.get("/")
def obtain_work_orders():
    """
    Get Unit Status and Parts for a Work Order
    ---
    tags:
      - Work Orders
    summary: Retrieve all units and their station-level part statuses and comments for a given work order.
    parameters:
      - name: work_order_id
        in: path
        required: true
        description: Numeric ID of the work order (e.g., 1 for WO0000001)
        schema:
          type: integer
    responses:
      200:
        description: Units and station data retrieved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                is_completed:
                  type: boolean
                  example: false
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
                            unit_status:
                              type: string
                              enum: ["not_started", "in_progress", "completed", "alert", "hold"]
                              example: "in_progress"
                            station_status:
                              type: string
                              enum: ["not_started", "in_progress", "completed", "alert", "hold"]
                              example: "in_progress"
                            station_comments:
                              type: string
                              example: "Delay due to part shortage"
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
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Invalid work order ID format
      500:
        description: Server error while retrieving units
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Database connection failed
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
    summary: Retrieve units for a work order with station status, part info, and completion status
    description: |
      Returns an array of units belonging to a specific work order.
      Each unit contains its associated stations, statuses, comments, and part requirements.
      Also includes a flag indicating whether the overall work order is completed.
    parameters:
      - name: work_order_id
        in: path
        required: true
        description: Work order ID in the format WOXXXXXXX (e.g., WO0000001)
        type: string
    responses:
      200:
        description: Work order details with units and station progress
        schema:
          type: object
          properties:
            is_completed:
              type: boolean
              example: false
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
                        unit_status:
                          type: string
                          enum: ["not_started", "in_progress", "completed", "alert", "hold"]
                          example: "in_progress"
                        station_status:
                          type: string
                          enum: ["not_started", "in_progress", "completed", "alert", "hold"]
                          example: "completed"
                        station_comments:
                          type: string
                          example: "Waiting on inspection"
                        part_number:
                          type: string
                          example: "200-00001"
                        part_description:
                          type: string
                          example: "Car Door"
                        quantity_required:
                          type: number
                          format: float
                          example: 4
                        quantity_supplied:
                          type: number
                          format: float
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
    id_part = work_order_id[2:]
    if not id_part or not id_part.isdigit():
        return jsonify({"error": "Invalid work order ID format"}), 400

    integer_work_order_id = int(id_part)
    response = retrieve_units_by_work_order_id(integer_work_order_id)
    return response


@work_orders_bp.post("/create_workorder")
def create_work_order():
    """
    Create a New Work Order
    ---
    tags:
      - Work Orders
    summary: Create a new work order and initialize required parts and statuses.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - product_number
            - quantity
          properties:
            product_number:
              type: string
              example: "100-00001"
            quantity:
              type: integer
              example: 10
    responses:
      201:
        description: Work order successfully created
        schema:
          type: object
          properties:
            message:
              type: string
              example: Work order created
            work_order_id:
              type: string
              example: WO0000001
      400:
        description: Bad request (e.g. missing fields or invalid format)
      500:
        description: Server error
    """
    data = request.get_json()
    response = add_work_order(data)
    return response


@work_orders_bp.post("/complete")
def complete_work_order():
    """
    Mark Work Order as Complete
    ---
    tags:
      - Work Orders
    summary: Marks a work order as complete if all stations have finished
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
          properties:
            work_order_id:
              type: string
              example: "WO0000001"
              description: The work order ID in display format
    responses:
      200:
        description: Work order marked as complete
        schema:
          type: object
          properties:
            message:
              type: string
              example: Work order marked as complete
            work_order_id:
              type: string
              example: WO0000001
      400:
        description: Work order not ready or invalid format
        schema:
          type: object
          properties:
            message:
              type: string
              example: Work order is not ready to be marked complete
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
    response = post_completion(data)
    return response
