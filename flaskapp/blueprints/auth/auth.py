import requests
from flask import request, jsonify, redirect, make_response, render_template, flash, current_app as app, url_for
from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, \
    jwt_refresh_token_required, get_jwt_identity, unset_jwt_cookies, unset_access_cookies, get_raw_jwt, jwt_required

from flaskapp import db, jwt
from flaskapp.blueprints.auth import auth_bp
from flaskapp.models.Model import User
from flaskapp.models.Schema import user_schema


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if get_jwt_identity() is None:
            return render_template('login.html')
        return redirect('/')

    email = request.form.get('email')
    password = request.form.get('password')
    user = authenticate(email, password)
    if not user:
        flash('No user was found with the given credentials.' , 'danger')
        return redirect(url_for('auth.login'))
    access_token = create_access_token(identity=user.identity)
    refresh_token = create_refresh_token(identity=user.identity)
    resp = make_response(redirect('/'))

    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp


def authenticate(email, password):
    user = User.lookup(email)
    if user and user.check_password(password):
        return user
    return None

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if get_jwt_identity() is None:
            return render_template('register.html')
        return redirect('/')
    new_user = user_schema.load(request.form)
    if User.lookup(new_user.email):
        flash('User with given email already exists', 'danger')
        return redirect(url_for('auth.register'))
    db.session.add(new_user)
    db.session.commit()
    flash('User created successfully', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/token/refresh', methods=['GET', 'POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    resp = make_response(redirect('/'))
    set_access_cookies(resp, access_token)
    return resp


@auth_bp.route('/logout')
@jwt_required
def logout():
    resp = make_response(redirect(url_for('auth.login')))
    unset_jwt_cookies(resp)
    return resp


@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return redirect(url_for('auth.login'), 302)


@jwt.invalid_token_loader
def invalid_token_callback(callback):
    resp = make_response(redirect(url_for('auth.login')))
    unset_jwt_cookies(resp)
    return resp, 302


@jwt.expired_token_loader
def expired_token_callback(callback):
    # Expired auth header
    # cookies = request.cookies
    # del cookies[app.config['JWT_ACCESS_COOKIE_NAME']]
    # resp = requests.get(f'{app.config["BASE_URL"]}{url_for("auth.refresh")}', cookies=cookies)
    res = make_response(redirect(f'{url_for("auth.refresh")}'))
    unset_access_cookies(res)
    # res.cookies = resp.cookies
    return res


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.identify(identity)