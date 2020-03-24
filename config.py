import os

# from dotenv import load_dotenv
#
basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    BASE_URL = 'https://file-exchange-ukma.herokuapp.com/'

    JWT_TOKEN_LOCATION = ['cookies']
    JWT_REFRESH_COOKIE_PATH = '/token/refresh'
    JWT_CSRF_CHECK_FORM = True
    JWT_SECRET_KEY = os.environ.get('SECRET_KEY') or 'somesecretstuff'


    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
    S3_BUCKET = os.environ.get('S3_BUCKET')
    AWS_REGION = 'eu-central-1'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secretsecret'
    DEBUG = os.environ.get('DEBUG') or False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                                'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_FILE_SIZE = 10**7 # 10 mb = 10**7
