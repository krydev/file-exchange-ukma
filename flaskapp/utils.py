import base64
import uuid

import arrow

from flask import current_app as app

def generate_uuid_str():
    return uuid.uuid4().hex

def generate_obj_name(file_id, file_name, user_id):
    return f"{user_id}/{file_id}_{file_name}"


def extract_file_name(obj_name):
    return obj_name.split("/", 1)[-1].split("_", 1)[-1]


def encode_key(obj_name):
    return base64.urlsafe_b64encode(obj_name.encode("utf-8"))\
                .decode("utf-8").strip("=")


def decode_key(obj_name):
    return base64.urlsafe_b64decode(obj_name + '=' * (4 - len(obj_name) % 4))\
                .decode("utf-8")


def get_file_size(file):
    file.seek(0, 2)
    return file.tell()


def datetimeformat(date, past=True):
    if past:
        dt = arrow.get(date)
        return dt.humanize()
    now = arrow.utcnow()
    return date.humanize(now)


def strip_domain(email):
    return email.split('@')[0]