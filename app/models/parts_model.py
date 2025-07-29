from app.db import connection
from flask import jsonify

GET_ALL_PRODUCTS = """
SELECT
    product_number,
    description
FROM
    Products
ORDER BY
    product_number;
"""


def get_all_products():
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL_PRODUCTS)
                rows = cursor.fetchall()
                products = [
                    {"product_number": row[0], "description": row[1]} for row in rows
                ]
                return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


GET_ALL_NEEDED_PARTS = """
SELECT
    CONCAT('WO', LPAD(CAST(wop.work_order_id AS TEXT), 7, '0')) AS work_order,
    wop.part_number,
    p.description,
    wop.quantity_needed AS quantity_required,
    COALESCE(wop.quantity_supplied, 0) AS quantity_supplied
FROM WorkOrderParts wop
JOIN Parts p ON wop.part_number = p.part_number
ORDER BY wop.work_order_id, wop.part_number;
"""


def get_needed_parts():
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL_NEEDED_PARTS)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                report = [dict(zip(columns, row)) for row in rows]

                return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


INSERT_PART_REQUEST = """
INSERT INTO PartRequests (
            work_order_id,
            station_number,
            part_number,
            quantity_requested,
            requested_by
        )
        VALUES (%s, %s, %s, %s, %s)
        RETURNING request_id, work_order_id, station_number, part_number, quantity_requested, request_date, status;
"""


def add_part_request(data):
    work_order_str = data["work_order_id"]
    if not work_order_str.startswith("WO") or not work_order_str[2:].isdigit():
        return jsonify({"error": "Invalid work_order_id format"}), 400

    work_order_id = int(work_order_str[2:])

    station_number = data["station_number"]
    part_number = data["part_number"]
    quantity_requested = data["quantity_requested"]
    requested_by = data["requested_by"]

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    INSERT_PART_REQUEST,
                    (
                        work_order_id,
                        station_number,
                        part_number,
                        quantity_requested,
                        requested_by,
                    ),
                )
                result = cursor.fetchone()

        return (
            jsonify(
                {
                    "message": "Part request created",
                    "request": {
                        "request_id": result[0],
                        "work_order_id": result[1],
                        "station_number": result[2],
                        "part_number": result[3],
                        "quantity_requested": float(result[4]),
                        "request_date": result[5].isoformat(),
                        "status": result[6],
                    },
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
