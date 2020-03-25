import operator

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from flaskapp import utils
from flaskapp.api import api
from flask_restful import Resource
import json
from flask import current_app as app, request
from flask_jwt_extended import get_jwt_identity, jwt_required

session = boto3.Session(
    region_name=app.config['AWS_REGION'],
    aws_access_key_id=app.config['AWS_ACCESS_KEY'],
    aws_secret_access_key=app.config['AWS_SECRET_KEY']
)


@api.resource('/files')
class FileListRes(Resource):
    method_decorators = [jwt_required]

    def get(self):
        s3_resource = session.resource('s3')
        my_bucket = s3_resource.Bucket(app.config['S3_BUCKET'])
        fl = [utils.file_summary(f) for f in my_bucket.objects.filter(Prefix=f'{get_jwt_identity()}/')]
        fl_sorted = [obj for obj in sorted(fl, key=operator.itemgetter('last_modified'), reverse=True)]
        return {'file_list': json.dumps(fl_sorted, default=str)}


@api.resource('/files/<string:key>')
class FileRes(Resource):
    method_decorators = [jwt_required]

    def get(self, key):
        # Generate a presigned URL for the S3 object
        object_name = utils.decode_key(key)
        s3_client = session.client('s3')
        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': app.config['S3_BUCKET'],
                                                                'Key': object_name},
                                                        ExpiresIn=3600)
        except ClientError:
            return {'error': 'File not found.'}, 404

        # The response contains the presigned URL
        return {'url': response}, 200

    def put(self, key):
        object_name = utils.decode_key(key)
        s3 = session.client('s3', config=Config(signature_version='s3v4'))
        fields = {
                'acl': 'private',
                'Content-Type': request.form['fileType'],
                'ContentDisposition': f'attachment; filename="{request.form["fileName"]}"'
            }
        response = s3.generate_presigned_post(
            Bucket=app.config['S3_BUCKET'],
            Key=object_name,
            Fields=fields,
            Conditions=[{'acl': 'private'}, {'Content-Type': request.form['fileType']}],
            ExpiresIn=3600
        )
        print(response)
        return response


    def delete(self, key):
        object_name = utils.decode_key(key)
        s3 = session.resource('s3')
        try:
            obj = s3.Object(app.config['S3_BUCKET'], object_name)
            obj.delete()
        except ClientError:
            return {'error': 'File not found.'}, 404

        return {}, 204
