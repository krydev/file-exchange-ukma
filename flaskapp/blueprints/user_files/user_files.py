import base64
import json
import uuid

import requests
from flask_jwt_extended import get_raw_jwt, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename, redirect

from flaskapp import utils
from flaskapp.api import api
from flaskapp.api.s3_utils import FileRes, FileListRes

from flask import request, current_app as app, render_template, flash, make_response

from flaskapp.blueprints.user_files import files_bp
from flaskapp.utils import generate_uuid_str


@files_bp.route('/')
@files_bp.route('/myfiles')
@jwt_required
def list_files():
    summaries = requests.get(f'{app.config["BASE_URL"]}{api.url_for(FileListRes)}',
                             cookies=request.cookies).json()
    headers = {'Content-Type': 'text/html'}
    return make_response(
        render_template('index.html',
                        files=json.loads(summaries['file_list']),
                        max_size=app.config["MAX_FILE_SIZE"],
                        csrf_token=(get_raw_jwt() or {}).get("csrf")
                        ), 200, headers)


@files_bp.route('/upload', methods=['POST'])
@jwt_required
def upload_file():
    if "file" not in request.files:
        flash('No file key in request.files', 'danger')
        return redirect('/') # 400

    file = request.files["file"]

    # There is no file selected to upload
    if file.filename == "":
        flash('No file has been selected', 'danger')
        return redirect('/') # 400

    if utils.get_file_size(file) > app.config["MAX_FILE_SIZE"]:
        flash('The file is too large', 'danger')
        return redirect('/') # 422

    # File is selected, upload to S3 and redirect to file page
    if file:
        file.filename = secure_filename(file.filename)
        object_name = utils.encode_key(
            utils.generate_obj_name(generate_uuid_str(), file.filename, get_jwt_identity())
        )
        file.seek(0)
        resp = requests.put(f'{app.config["BASE_URL"]}{api.url_for(FileRes, key=object_name)}',
                            files={'file': (file.filename, file.stream,
                                    file.content_type, file.headers)},
                            data=request.form, cookies=request.cookies)

        if resp.status_code == 201:
            flash('File uploaded successfully', "info")
            return redirect('/')
        flash('File couldn\'t be uploaded', 'danger')
        return redirect('/') # 500

    flash('No file has been selected', 'danger')
    return redirect('/')  # 400


@files_bp.route('/myfiles/<string:key>/download')
@jwt_required
def download_file(key):
    # uuid.UUID(file_id)
    resp = requests.get(f'{app.config["BASE_URL"]}{api.url_for(FileRes, key=key)}',
                        cookies=request.cookies).json()
    if resp.get('error'):
        flash('File has expired or doesn\'t exist', 'danger')
        return redirect("/")
    return redirect(resp['url'])


@files_bp.route('/myfiles/<string:key>/delete', methods=['POST'])
@jwt_required
def delete_file(key):
    resp = requests.delete(f'{app.config["BASE_URL"]}{api.url_for(FileRes, key=key)}',
                           data=request.form, cookies=request.cookies)
    if resp.status_code > 300:
        flash('File has expired or doesn\'t exist', 'danger')
    else: flash('File deleted successfully', 'info')
    return redirect("/")