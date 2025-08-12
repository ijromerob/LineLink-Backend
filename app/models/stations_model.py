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
    work_order_str = data["work_order_id"]
    if not work_order_str.startswith("WO") or not work_order_str[2:].isdigit():
        return jsonify({"error": "Invalid work_order_id format"}), 400

    work_order_id = int(work_order_str[2:])
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


UPDATE_UNIT_STATION_STATUS = """
UPDATE UnitStationStatus
SET status = %s, updated_at = NOW()
WHERE work_order_id = %s AND unit_number = %s AND station_number = %s
"""


def update_station_status(
    work_order_str,
    unit_number,
    station_number,
    new_status,
):

    if not work_order_str.startswith("WO") or not work_order_str[2:].isdigit():
        return jsonify({"error": "Invalid work_order_id format"}), 400

    work_order_id = int(work_order_str[2:])
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    UPDATE_UNIT_STATION_STATUS,
                    (new_status, work_order_id, unit_number, station_number),
                )

                return jsonify({"message": "Status updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
