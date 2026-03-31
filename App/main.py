import os
from flask import Flask, flash, redirect, render_template, url_for
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask_jwt_extended import unset_jwt_cookies

from App.database import init_db
from App.config import load_config


from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views, setup_admin



def add_views(app):
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    CORS(app)
    add_auth_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    jwt = setup_jwt(app)
    setup_admin(app)
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    @jwt.expired_token_loader
    @jwt.needs_fresh_token_loader
    def custom_unauthorized_response(error):
        response = redirect(url_for('index_views.index_page'))
        # If the user token is expired/invalid, clear the stored JWT cookies
        # so they don't keep getting redirected in a loop.
        try:
            unset_jwt_cookies(response)
        except Exception:
            # Best-effort only; do not block redirect if cookie unsetting fails.
            pass
        flash("Session expired. Please log in again.")
        return response, 302
    app.app_context().push()
    return app