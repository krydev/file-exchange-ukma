from flask import Blueprint
from flask_restful import Api

s3_bp = Blueprint('s3_utils', __name__, url_prefix='/api')
api = Api(s3_bp)

from flaskapp.api import s3_utils
