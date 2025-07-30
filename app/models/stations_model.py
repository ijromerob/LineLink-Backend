import jwt
from datetime import datetime, timedelta
from app.db import connection
from flask import jsonify
from app.config import Config


INSERT_NEW_COMMENT = """
INSERT INTO WorkOrderStationStatus (work_order_id, station_number, notes, updated_at)
        VALUES (%s, %s, %s, now())
        ON CONFLICT (work_order_id, station_number)
        DO UPDATE SET
          notes = EXCLUDED.notes,
          updated_at = now();
"""


def post_comment(data):
    work_order_id = data["work_order_id"]
    station_number = data["station_number"]
    comment = data["comment"]

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    INSERT_NEW_COMMENT, (work_order_id, station_number, comment)
                )
                return jsonify({"message": "Comment added/updated successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
