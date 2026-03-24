from flask import request

from App.controllers import store_supplementary_uploads


def int_list_from_form(name):
    values = []
    for value in request.form.getlist(name):
        if not value:
            continue
        values.append(int(value))
    return values


def supplementary_files_from_form():
    text_value = request.form.get("supplementary_files", "")
    return [part.strip() for part in text_value.split(",") if part.strip()]


def combined_supplementary_files():
    uploaded = request.files.getlist("supplementary_uploads")
    stored_names = store_supplementary_uploads(uploaded)
    return supplementary_files_from_form() + stored_names
