from app import db


class Resume(db.Model):

    __tablename__ = "resumes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    resume_text = db.Column(
        db.Text,
        nullable=False
    )

    ats_score = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "resumes",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Resume {self.filename}>"
