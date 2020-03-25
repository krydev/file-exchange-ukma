import boto3
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
        s3_resource = session.resource("s3")
        my_bucket = s3_resource.Bucket(app.config["S3_BUCKET"])
        fl = [utils.file_summary(f) for f in my_bucket.objects.filter(Prefix=f"{get_jwt_identity()}/")]
        return {'file_list': json.dumps(fl, default=str)}


@api.resource('/files/<string:key>')
class FileRes(Resource):
    method_decorators = [jwt_required]

    def get(self, key):
        # Generate a presigned URL for the S3 object
        object_name = utils.decode_key(key)
        s3_client = session.client("s3")
        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': app.config["S3_BUCKET"],
                                                                'Key': object_name},
                                                        ExpiresIn=3600)
        except ClientError:
            return {'error': 'File not found.'}, 404

        # The response contains the presigned URL
        return {'url': response}, 200

    def put(self, key):
        object_name = utils.decode_key(key)
        file = request.files["file"]
        s3 = session.client("s3")
        s3_resource = session.resource("s3")
        try:
            # file.seek(0)
            s3.put_object(Body=file, Bucket=app.config["S3_BUCKET"], Key=object_name,
                          ContentDisposition=f"attachment; filename=\"{file.filename}\"")
        except ClientError:
            return {'error': 'There was an internal error.'}, 500
        summary = s3_resource.ObjectSummary(app.config["S3_BUCKET"], object_name)
        return {'success': 'File has been uploaded successfully',
                'file_list': json.dumps([utils.file_summary(summary)])}, 201

    def delete(self, key):
        object_name = utils.decode_key(key)
        s3 = session.resource("s3")
        try:
            obj = s3.Object(app.config["S3_BUCKET"], object_name)
            obj.delete()
        except ClientError:
            return {'error': 'File not found.'}, 404

        return {}, 204

# response = s3.generate_presigned_post(
#     Bucket=app.config["S3_BUCKET"],
#     Key=object_name,
#     Fields={"acl": "public-read", "Content-Type": file.content_type},
#     Conditions=[
#         {"acl": "public-read"},
#         {"Content-Type": file.content_type}
#     ],
#     ExpiresIn=3600
# )
#
# with open(object_name, 'rb') as f:
#     files = {'file': (object_name, f)}
#     http_response = requests.post(response['url'], data=response['fields'], files=files)
# return http_response