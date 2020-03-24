from flask import Blueprint

files_bp = Blueprint('user_files', __name__)

from flaskapp.blueprints.user_files import user_files