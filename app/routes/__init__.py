from .auth.oauth_routes import auth_bp
from .users import users_bp
from .work_orders import work_orders_bp
from .parts import parts_bp
from .stations import stations_bp
from .warehouse import warehouse_bp


def register_blueprints(app):
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(work_orders_bp, url_prefix="/api/workorders")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(parts_bp, url_prefix="/api/parts")
    app.register_blueprint(stations_bp, url_prefix="/api/stations")
    app.register_blueprint(warehouse_bp, url_prefix="/api/warehouse")
