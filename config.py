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

    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:

        # Render and some PostgreSQL providers may expose
        # the connection string using the postgres:// scheme.
        # SQLAlchemy expects postgresql://.

        if DATABASE_URL.startswith("postgres://"):

            DATABASE_URL = DATABASE_URL.replace(
                "postgres://",
                "postgresql://",
                1
            )

        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    else:

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
    # Production HTTPS can enable this through
    # an environment-specific configuration later.

    SESSION_COOKIE_SECURE = False