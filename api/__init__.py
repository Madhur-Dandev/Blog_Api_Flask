from flask import Blueprint
from .auth import auth
from .blogs import blogs
from .profile import profile

api = Blueprint("api", __name__, url_prefix="/api")
api.register_blueprint(auth)
api.register_blueprint(blogs)
api.register_blueprint(profile)