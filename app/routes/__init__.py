from .auth import auth_bp
from .users import users_bp
from .work_orders import work_orders_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(work_orders_bp, url_prefix="/api/workorders")
