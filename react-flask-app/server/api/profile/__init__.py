from flask import Blueprint

bp = Blueprint('profile', __name__)

from api.profile import routes
