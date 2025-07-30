from app.db import connection
from flask import jsonify

INSERT_NEW_DISPATCH = """
INSERT INTO PartSupplyLog (
                        work_order_id, station_number, part_number, quantity_supplied, supplied_at
                    ) VALUES (%s, %s, %s, %s, NOW())
                    RETURNING supply_id;
"""


def post_dispatch_parts(data):
    work_order_str = data["work_order_id"]
    if not work_order_str.startswith("WO") or not work_order_str[2:].isdigit():
        return jsonify({"error": "Invalid work_order_id format"}), 400

    work_order_id = int(work_order_str[2:])

    station_number = data["station_number"]
    part_number = data["part_number"]
    quantity_supplied = data["quantity_supplied"]

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    INSERT_NEW_DISPATCH,
                    (work_order_id, station_number, part_number, quantity_supplied),
                )
                supply_id = cursor.fetchone()[0]
        return (
            jsonify(
                {
                    "message": "Part dispatch recorded successfully.",
                    "supply_id": supply_id,
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
