from flask_jwt_extended import get_raw_jwt, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename, redirect

from flaskapp import utils, q
from flaskapp.api import api
from flaskapp.api.s3_utils import FileRes, FileListRes

from flask import request, current_app as app, render_template, jsonify
from flaskapp.blueprints.user_files import files_bp
from flaskapp.utils import generate_uuid_str, humansize


@files_bp.route('/')
@jwt_required
def index():
    return render_template('index.html',
                           max_size=humansize(app.config["MAX_FILE_SIZE"]),
                           csrf_token=(get_raw_jwt() or {}).get("csrf")
                       )


@files_bp.route('/myfiles')
@jwt_required
def list_files():
    job = q.enqueue(utils.request_json, 'GET',
                    url=f'{app.config["BASE_URL"]}{api.url_for(FileListRes)}',
                    cookies=request.cookies,
                    headers={'Content-Type': 'application/json'})
    return jsonify({'task_id': job.get_id()}), 202


@files_bp.route('/upload', methods=['POST'])
@jwt_required
def upload_file():
    # There is no file selected to upload
    filename = request.form['fileName']
    if filename == "":
        return jsonify({'error': 'No file has been selected'}), 400

    if int(request.form['fileSize']) > app.config["MAX_FILE_SIZE"]:
        return jsonify({'error': 'The file is too large'}), 422

    filename = secure_filename(filename)
    object_name = utils.encode_key(
        utils.generate_obj_name(generate_uuid_str(), filename, get_jwt_identity())
    )
    job = q.enqueue(utils.request_json,'PUT',
                    url=f'{app.config["BASE_URL"]}{api.url_for(FileRes, key=object_name)}',
                    data=request.form, cookies=request.cookies)
    return jsonify({'task_id': job.get_id()}), 202


@files_bp.route('/myfiles/<string:key>/download')
@jwt_required
def download_file(key):
    job = q.enqueue(utils.request_json, 'GET',
                    url=f'{app.config["BASE_URL"]}{api.url_for(FileRes, key=key)}',
                    cookies=request.cookies,
                    headers={'Content-Type': 'application/json'})
    return jsonify({'task_id': job.get_id()}), 202


@files_bp.route('/myfiles/<string:key>/delete', methods=['POST'])
@jwt_required
def delete_file(key):
    job = q.enqueue(utils.request_json, 'DELETE',
                    url=f'{app.config["BASE_URL"]}{api.url_for(FileRes, key=key)}',
                    data=request.form, cookies=request.cookies,
                    headers={'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': request.form['csrf_token']})
    return jsonify({'task_id': job.get_id()}), 202


@files_bp.route('/tasks/<task_id>')
@jwt_required
def get_task_result(task_id):
    job = q.fetch_job(task_id)
    if job.is_finished:
        resp = {'data': job.result, 'csrf_token': (get_raw_jwt() or {}).get("csrf")}
        return jsonify(resp), 200
    return {}, 202