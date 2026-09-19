from flask import (
    Blueprint,
    render_template,
)

from app.models.resume import Resume
from app.utils.helpers import login_required


dashboard = Blueprint(
    "dashboard",
    __name__
)


@dashboard.route(
    "/dashboard"
)
@login_required
def index():

    from flask import session

    resumes = (
        Resume.query
        .filter_by(
            user_id=session["user_id"]
        )
        .order_by(
            Resume.created_at.desc()
        )
        .all()
    )

    return render_template(
        "pages/dashboard.html",
        user_name=session.get(
            "user_name",
            "User"
        ),
        resumes=resumes
    )