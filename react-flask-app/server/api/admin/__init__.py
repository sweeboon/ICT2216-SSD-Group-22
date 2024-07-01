from flask import Blueprint

bp = Blueprint('admin', __name__)

from api.admin import routes
