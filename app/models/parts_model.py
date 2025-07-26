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
