from app.db import connection
from flask import jsonify

GET_ALL_WORK_ORDERS_SUMMARY = """
SELECT
  wo.work_order_id,
  'WO' || LPAD(wo.work_order_id::text, 7, '0') AS formatted_work_order_id,
  wo.product_number,
  wo.quantity_to_produce,
  COUNT(wop.part_number) AS total_parts_needed,
  COUNT(CASE WHEN wop.quantity_supplied > 0 THEN 1 END) AS parts_supplied,
  COUNT(CASE WHEN wop.quantity_supplied = 0 THEN 1 END) AS parts_missing,
  wo.is_completed
FROM WorkOrders wo
JOIN WorkOrderParts wop ON wo.work_order_id = wop.work_order_id
GROUP BY wo.work_order_id, wo.product_number, wo.quantity_to_produce, wo.is_completed
ORDER BY wo.work_order_id ASC;
"""


def retrieve_work_orders():
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_ALL_WORK_ORDERS_SUMMARY)
                results = cursor.fetchall()
                work_orders = []
                for row in results:
                    (
                        work_order_id,
                        formatted_work_order_id,
                        product_number,
                        quantity_to_produce,
                        total_parts_needed,
                        parts_supplied,
                        parts_missing,
                        is_completed,
                    ) = row
                    work_orders.append(
                        {
                            "work_order_id": formatted_work_order_id,
                            "product_number": product_number,
                            "quantity_to_produce": quantity_to_produce,
                            "total_parts_needed": total_parts_needed,
                            "parts_supplied": parts_supplied,
                            "parts_missing": parts_missing,
                            "is_completed": is_completed,
                        }
                    )
        return jsonify({"work_orders": work_orders}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


GET_WORK_ORDER_BY_ID = """
SELECT
  uss.unit_number,
  uss.station_number,
  uss.status AS unit_status,
  swop.part_number,
  p.description AS part_description,
  swop.quantity_needed AS quantity_required,
  swop.quantity_supplied,
  woss.status AS station_status,
  woss.notes AS station_comments,
  wo.is_completed
FROM UnitStationStatus uss
JOIN StationWorkOrderParts swop
  ON swop.work_order_id = uss.work_order_id
  AND swop.station_number = uss.station_number
JOIN Parts p
  ON swop.part_number = p.part_number
JOIN WorkOrderStationStatus woss
  ON woss.work_order_id = uss.work_order_id
  AND woss.station_number = uss.station_number
JOIN WorkOrders wo
  ON wo.work_order_id = uss.work_order_id
WHERE uss.work_order_id = %s
ORDER BY uss.unit_number, uss.station_number;
"""


def retrieve_units_by_work_order_id(work_order_id):

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(GET_WORK_ORDER_BY_ID, (work_order_id,))
                results = cursor.fetchall()
                units_dict = {}

                is_completed = results[0][-1]
                for (
                    unit_number,
                    station_number,
                    unit_status,
                    part_number,
                    part_description,
                    quantity_required,
                    quantity_supplied,
                    station_status,
                    station_comments,
                    is_completed,
                ) in results:
                    if unit_number not in units_dict:
                        units_dict[unit_number] = {
                            "unit_number": unit_number,
                            "stations": [],
                        }

                    units_dict[unit_number]["stations"].append(
                        {
                            "station_number": station_number,
                            "unit_status": unit_status,
                            "station_status": station_status,
                            "station_comments": station_comments,
                            "part_number": part_number,
                            "part_description": part_description,
                            "quantity_required": float(quantity_required),
                            "quantity_supplied": float(quantity_supplied),
                        }
                    )

                units = list(units_dict.values())

                return jsonify({"units": units, "is_completed": is_completed}), 200

    except ValueError:
        return jsonify({"error": "Invalid work order ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


INSERT_NEW_WORK_ORDER = """
INSERT INTO WorkOrders (product_number, quantity_to_produce)
VALUES (%s, %s)
RETURNING work_order_id;
"""

INSERT_NEW_WORKORDER_PARTS = """
INSERT INTO WorkOrderParts (work_order_id, part_number, quantity_needed)
SELECT
    %s AS work_order_id,
    b.part_number,
    b.quantity * %s AS quantity_needed
FROM BOM b
WHERE b.product_number = %s;
"""

INSERT_NEW_WORKSTATION_PARTS = """
INSERT INTO StationWorkOrderParts (
    work_order_id, station_number, part_number, quantity_needed
)
SELECT
    %s AS work_order_id,
    sp.station_number,
    sp.part_number,
    sp.quantity_required * %s AS quantity_needed
FROM BOM b
JOIN StationParts sp ON b.part_number = sp.part_number
WHERE b.product_number = %s;
"""

INITIALIZE_STATUS = """
INSERT INTO WorkOrderStationStatus (work_order_id, station_number, status)
SELECT
    %s,
    s.station_number,
    'not_started'::station_status
FROM Stations s;
"""


def add_work_order(data):
    product_number = data["product_number"]
    quantity = data["quantity"]

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(INSERT_NEW_WORK_ORDER, (product_number, quantity))
                work_order_id = cursor.fetchone()[0]

                cursor.execute(
                    INSERT_NEW_WORKORDER_PARTS,
                    (work_order_id, quantity, product_number),
                )

                cursor.execute(
                    INSERT_NEW_WORKSTATION_PARTS,
                    (work_order_id, quantity, product_number),
                )

                cursor.execute(INITIALIZE_STATUS, (work_order_id,))

        return (
            jsonify(
                {
                    "message": "Work order created",
                    "work_order_id": f"WO{work_order_id:07d}",
                }
            ),
            201,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


UPDATE_WORK_ORDER_COMPLETE = """
UPDATE WorkOrders
SET is_completed = TRUE
WHERE work_order_id = %s
  AND NOT EXISTS (
    SELECT 1 FROM WorkOrderStationStatus
    WHERE work_order_id = %s AND status != 'completed'
  )
RETURNING work_order_id;
"""


def post_completion(data):
    work_order_str = data["work_order_id"]
    if not work_order_str.startswith("WO") or not work_order_str[2:].isdigit():
        return jsonify({"error": "Invalid work_order_id format"}), 400

    work_order_id = int(work_order_str[2:])

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    UPDATE_WORK_ORDER_COMPLETE, (work_order_id, work_order_id)
                )
                result = cursor.fetchone()
                if result:
                    return (
                        jsonify(
                            {
                                "message": "Work order marked as complete",
                                "work_order_id": f"WO{result[0]:07d}",
                            }
                        ),
                        200,
                    )
                else:
                    return (
                        jsonify(
                            {"message": "Work order is not ready to be marked complete"}
                        ),
                        400,
                    )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


INSERT_COMMENT_PER_STATION = """
UPDATE UnitStationStatus
SET notes = %s, updated_at = NOW()
WHERE work_order_id = %s AND unit_number = %s AND station_number = %s
"""


def post_comment(work_order_id, unit_number, station_number, data):
    try:
        work_order_id_int = int(work_order_id[2:])
        comment = data["comment"]

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    INSERT_COMMENT_PER_STATION,
                    (comment, work_order_id_int, unit_number, station_number),
                )
                if cursor.rowcount == 0:
                    return jsonify({"error": "Record not found"}), 404

        return jsonify({"message": "Comment updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
