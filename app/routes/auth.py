from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from sqlalchemy.exc import IntegrityError

from app import db
from app.models.user import User


auth = Blueprint(
    "auth",
    __name__
)


# =====================================================
# REGISTER
# =====================================================

@auth.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        # ---------------------------------------------
        # Validate fields
        # ---------------------------------------------

        if not name or not email or not password:

            flash(
                "Please fill in all fields.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ---------------------------------------------
        # Validate password
        # ---------------------------------------------

        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ---------------------------------------------
        # Check existing user
        # ---------------------------------------------

        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ---------------------------------------------
        # Create user
        # ---------------------------------------------

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(
                password
            )
        )


        db.session.add(user)


        # ---------------------------------------------
        # Save user safely
        # ---------------------------------------------

        try:

            db.session.commit()

        except IntegrityError:

            db.session.rollback()

            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )

        except Exception:

            db.session.rollback()

            flash(
                "Unable to create the account right now. "
                "Please try again.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        flash(
            "Account created successfully. "
            "You can now log in.",
            "success"
        )


        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "pages/register.html"
    )


# =====================================================
# LOGIN
# =====================================================

@auth.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # Checkbox sends "on" when checked
        # and sends nothing when unchecked.
        remember = (
            request.form.get("remember") == "on"
        )


        # ---------------------------------------------
        # Find user
        # ---------------------------------------------

        user = User.query.filter_by(
            email=email
        ).first()


        # ---------------------------------------------
        # Check account
        # ---------------------------------------------

        if user and check_password_hash(
            user.password,
            password
        ):

            # -----------------------------------------
            # Start a fresh session
            # -----------------------------------------

            session.clear()


            # -----------------------------------------
            # Store authenticated user
            # -----------------------------------------

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email


            # -----------------------------------------
            # Remember Me
            # -----------------------------------------

            session.permanent = remember


            # -----------------------------------------
            # Go to resume upload
            # -----------------------------------------

            return redirect(
                url_for("resume.upload")
            )


        # ---------------------------------------------
        # Invalid login
        # ---------------------------------------------

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "pages/login.html"
    )


# =====================================================
# LOGOUT
# =====================================================

@auth.route(
    "/logout"
)
def logout():

    session.clear()


    flash(
        "You have been logged out.",
        "success"
    )


    return redirect(
        url_for("home.index")
    )