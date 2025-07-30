from flask import Blueprint, request
from app.models.stations_model import post_comment

stations_bp = Blueprint("stations", __name__)


@stations_bp.post("/comment")
def add_comment():
    """
    Add or Update a Comment on a Station for a Work Order
    ---
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
              type: integer
              example: 1
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
