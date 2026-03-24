from flask import Blueprint


workflow_views = Blueprint("workflow_views", __name__)


from . import admin_workflow  # noqa: E402,F401
from . import attendee_workflow  # noqa: E402,F401
from . import author_workflow  # noqa: E402,F401
from . import workflow_files  # noqa: E402,F401
from . import judge_workflow  # noqa: E402,F401
from . import reviewer_workflow  # noqa: E402,F401
from . import usher_workflow  # noqa: E402,F401
