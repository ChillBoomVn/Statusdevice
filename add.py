
from flask import Flask, flash, redirect, url_for, render_template, request, session
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from os import path
from add import add_number

app = Flask(__name__)
app.config["SECRET_KEY"] = "asdfghjkl"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///status.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=1)

db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email


@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    return render_template("home.html")


@app.route("/user", methods=["POST", "GET"])
def user():
    if "user" in session:
        name = session["user"]
        if request.method == "POST":
            if not request.form["email"] and request.form["name"]:
                User.query.filter_by(name=name).delete()
                db.session.commit()
                flash("Deleted user!")
                return redirect(url_for("log_out"))
            else:
                email = request.form["email"]
                session["email"] = email
                found_user = User.query.filter_by(name=name).first()
                found_user.email = email
                db.session.commit()
                flash("Email updated!")
        elif "email" in session:
            email = session["email"]
        return render_template("user.html", user=name, email=email)
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def log_out():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    if not path.exists("user.db"):
        with app.app_context():  # Tạo ngữ cảnh ứng dụng
            db.create_all()
            print("Created database!")
    app.run(debug=True)