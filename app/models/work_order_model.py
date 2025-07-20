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
  COUNT(CASE WHEN wop.quantity_supplied = 0 THEN 1 END) AS parts_missing
FROM WorkOrders wo
JOIN WorkOrderParts wop ON wo.work_order_id = wop.work_order_id
GROUP BY wo.work_order_id, wo.product_number, wo.quantity_to_produce
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
                    ) = row
                    work_orders.append(
                        {
                            "work_order_id": formatted_work_order_id,
                            "product_number": product_number,
                            "quantity_to_produce": quantity_to_produce,
                            "total_parts_needed": total_parts_needed,
                            "parts_supplied": parts_supplied,
                            "parts_missing": parts_missing,
                        }
                    )
        return jsonify({"work_orders": work_orders}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


GET_WORK_ORDER_BY_ID = """
SELECT
  uss.unit_number,
  uss.station_number,
  uss.status,
  swop.part_number,
  p.description AS part_description,
  swop.quantity_needed AS quantity_required,
  swop.quantity_supplied
FROM UnitStationStatus uss
JOIN StationWorkOrderParts swop
  ON swop.work_order_id = uss.work_order_id
  AND swop.station_number = uss.station_number
JOIN Parts p
  ON swop.part_number = p.part_number
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
                for (
                    unit_number,
                    station_number,
                    status,
                    part_number,
                    part_description,
                    quantity_required,
                    quantity_supplied,
                ) in results:
                    if unit_number not in units_dict:
                        units_dict[unit_number] = {
                            "unit_number": unit_number,
                            "stations": [],
                        }

                    units_dict[unit_number]["stations"].append(
                        {
                            "station_number": station_number,
                            "status": status,
                            "part_number": part_number,
                            "part_description": part_description,
                            "quantity_required": float(quantity_required),
                            "quantity_supplied": float(quantity_supplied),
                        }
                    )

                units = list(units_dict.values())
                return jsonify({"units": units}), 200

    except ValueError:
        return jsonify({"error": "Invalid work order ID format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
