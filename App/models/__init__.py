from .attendance import *
from .award import *
from .digest import *
from .feedback import *
from .judge_assignment import *
from .presentation import *
from .qr_code import *
from .review import *
from .review_submission import *
from .rsvp import *
from .score import *
from .session import *
from .submission import *
from .submission_author import *
from .submission_version import *
from .supplementary_material import *
from .track import *
from .user import *

# Backwards-compatible alias used by older tests and some legacy code paths.
ReviewAssignment = ReviewSubmission
