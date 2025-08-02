from flask import Blueprint, request
from app.models.work_order_model import (
    retrieve_work_orders,
    retrieve_units_by_work_order_id,
    add_work_order,
    post_completion,
    post_comment,
)

work_orders_bp = Blueprint("work_orders", __name__)


@work_orders_bp.get("/")
def obtain_work_orders():
    """
    Get all work orders summary
    ---
    tags:
      - Work Orders
    summary: Retrieve all work orders with part supply status
    description: |
      Returns a list of all work orders, including:
        - Work order ID
        - Product number
        - Quantity to produce
        - Total parts needed
        - Parts supplied
        - Parts missing
        - Completion status
    responses:
      200:
        description: Successfully retrieved work orders
        content:
          application/json:
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
                        example: 3
                      parts_missing:
                        type: integer
                        example: 1
                      is_completed:
                        type: boolean
                        example: false
      500:
        description: Server error while retrieving work orders
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Database connection failed"
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


@work_orders_bp.put(
    "/<work_order_id>/units/<int:unit_number>/stations/<station_number>/comment"
)
def update_unit_station_comment(work_order_id, unit_number, station_number):
    """
    Update comment for a specific unit at a station
    ---
    tags:
      - Work Orders
    summary: Add or update a comment for a unit at a specific station
    description: |
      Adds or updates a comment for a specific unit and station in a given work order.

    parameters:
      - name: work_order_id
        in: path
        required: true
        schema:
          type: string
        description: Work order ID (e.g., WO0000001)
      - name: unit_number
        in: path
        required: true
        schema:
          type: integer
        description: Unit number within the work order
      - name: station_number
        in: path
        required: true
        schema:
          type: string
        description: Station number (as string)
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - comment
          properties:
            comment:
              type: string
              example: "missing part 222-22222"
              description:

    responses:
      200:
        description: Comment successfully updated
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Comment updated successfully
      404:
        description: No matching record found to update
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Record not found
      500:
        description: Server error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Internal server error
    """
    data = request.get_json()
    response = post_comment(work_order_id, unit_number, station_number, data)
    return response
