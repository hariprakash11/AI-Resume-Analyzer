import os


BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


class Config:

    # =====================================================
    # APPLICATION SECRET
    # =====================================================

    SECRET_KEY = os.getenv("SECRET_KEY")

    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY environment variable is not configured."
        )


    # =====================================================
    # DATABASE
    # =====================================================

    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///"
        + os.path.join(
            BASE_DIR,
            "instance",
            "resume.db"
        )
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False


    # =====================================================
    # FILE UPLOADS
    # =====================================================

    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
    )

    MAX_CONTENT_LENGTH = (
        10 * 1024 * 1024
    )


    # =====================================================
    # SESSION SECURITY
    # =====================================================

    SESSION_COOKIE_HTTPONLY = True

    SESSION_COOKIE_SAMESITE = "Lax"

    # False for local HTTP development.
    # Change to True when deployed over HTTPS.
    SESSION_COOKIE_SECURE = False