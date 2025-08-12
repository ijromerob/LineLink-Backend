from flask import Blueprint, request
from app.models.stations_model import post_comment, update_station_status
from ..utils.jwt_helper import token_required

stations_bp = Blueprint("stations", __name__)


@stations_bp.post("/comment")
@token_required
def add_comment():
    """
    Add or Update a Comment on a Station for a Work Order
    ---
    security:
      - Bearer: []
    tags:
      - Stations
    summary: Add or update comments for a given station on a specific work order
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
            - comment
          properties:
            work_order_id:
              type: string
              example: WO0000001
              description: ID of the work order
            station_number:
              type: string
              example: "2"
              description: Station number
            comment:
              type: string
              example: "Waiting for parts"
              description: Comment or notes about this station's progress
    responses:
      201:
        description: Comment successfully added or updated
        schema:
          type: object
          properties:
            message:
              type: string
              example: Comment added/updated successfully
      400:
        description: Bad request (missing fields)
      500:
        description: Internal server error
    """
    data = request.get_json()
    response = post_comment(data)
    return response


@stations_bp.put(
    "/workorders/<string:work_order_id>/units/<int:unit_number>/stations/<string:station_number>/status"
)
def update_unit_station_status(work_order_id, unit_number, station_number):
    """
     Update the status and notes for a specific station in a specific unit of a work order
    ---
    tags:
      - Stations
    parameters:
      - name: work_order_id
        in: path
        required: true
        description: Work order identifier in the format `WO<number>` (e.g., `WO123`).
        type: string
        example: WO123
      - name: unit_number
        in: path
        required: true
        description: Unit number within the work order.
        type: integer
        example: 1
      - name: station_number
        in: path
        required: true
        description: Station number within the unit.
        type: string
        example: "1"
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum: [not_started, in_progress, completed, alert, hold]
              description: The new status for the station.
              example: in_progress
    responses:
      200:
        description: Status updated successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              example: Status updated successfully
      400:
        description: Bad request (invalid status, missing required fields, or invalid work_order_id format).
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Invalid status: xyz"
      500:
        description: Internal server error while updating status.
    """
    data = request.get_json()
    new_status = data.get("status")
    if not new_status:
        return {"message": "Status is required"}, 400

    allowed_statuses = ["in_progress", "completed", "not_started", "alert", "hold"]
    if new_status not in allowed_statuses:
        return {"message": f"Invalid status: {new_status}"}, 400

    response = update_station_status(
        work_order_id, unit_number, station_number, new_status
    )

    return response
