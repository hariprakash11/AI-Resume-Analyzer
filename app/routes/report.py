from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    session,
)

from app.models.resume import Resume
from app.services.report import build_report
from app.utils.helpers import login_required


report = Blueprint(
    "report",
    __name__
)


@report.route(
    "/report/<int:resume_id>"
)
@login_required
def view_report(resume_id):

    resume = (
        Resume.query
        .filter_by(
            id=resume_id,
            user_id=session["user_id"]
        )
        .first()
    )

    if resume is None:

        flash(
            "The requested resume analysis was not found.",
            "error"
        )

        return redirect(
            url_for("dashboard.index")
        )

    try:

        report_data = build_report(
            resume
        )

    except Exception:

        flash(
            "Unable to load the resume analysis.",
            "error"
        )

        return redirect(
            url_for("dashboard.index")
        )

    return render_template(
        "pages/report.html",
        **report_data
    )