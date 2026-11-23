import os
import re
import sqlite3
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash


EMAIL_PATTERN = re.compile(
    r"^(?=.{1,254}$)(?=.{1,64}@)"
    r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    r"(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
    r"@(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}$"
)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or os.urandom(32),
        DATABASE=os.environ.get(
            "DATABASE_PATH", str(Path(app.instance_path) / "users.sqlite")
        ),
    )
    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    def initialize_database():
        with sqlite3.connect(app.config["DATABASE"]) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    initialize_database()

    @app.get("/")
    def index():
        if "user_id" not in session:
            return redirect(url_for("signup"))
        return render_template("index.html", email=session["email"])

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if "user_id" in session:
            return redirect(url_for("index"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not EMAIL_PATTERN.fullmatch(email):
                flash("Enter a valid email address.", "error")
            elif len(password) < 8:
                flash("Password must be at least 8 characters long.", "error")
            else:
                try:
                    with sqlite3.connect(app.config["DATABASE"]) as connection:
                        cursor = connection.execute(
                            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                            (email, generate_password_hash(password)),
                        )
                        user_id = cursor.lastrowid
                except sqlite3.IntegrityError:
                    flash("An account with that email already exists.", "error")
                else:
                    session["user_id"] = user_id
                    session["email"] = email
                    flash("Registration successful. Welcome!", "success")
                    return redirect(url_for("index"))

        return render_template("signup.html", email=request.form.get("email", ""))

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("signup"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
