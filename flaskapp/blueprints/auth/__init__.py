from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from flaskapp.blueprints.auth import auth