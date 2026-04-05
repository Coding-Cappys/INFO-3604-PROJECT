from urllib.parse import urljoin, urlparse

from flask import request


def parse_int(value, default=None, minimum=None, maximum=None):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default

    if minimum is not None and parsed < minimum:
        return default
    if maximum is not None and parsed > maximum:
        return default
    return parsed


def parse_rating(value, default=3):
    return parse_int(value, default=default, minimum=1, maximum=5)


def safe_next_url(target):
    if not target:
        return None

    host_url = request.host_url
    ref = urlparse(host_url)
    test = urlparse(urljoin(host_url, target))

    if test.scheme in ("http", "https") and ref.netloc == test.netloc:
        return target
    return None
