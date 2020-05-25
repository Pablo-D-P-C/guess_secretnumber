from flask import Flask, request, render_template, make_response, redirect, url_for
from models import User, db
import hashlib
import random
import uuid


app = Flask(__name__)
db.create_all()


@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token, deleted=False).first()
    else:
        user = None

    return render_template("index.html", user=user)


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    password = request.form.get("user-password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    secret_number = random.randint(1, 30)
    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email, secret_number=secret_number, password=hashed_password)
        db.add(user)
        db.commit()

    if hashed_password != user.password:
        return "WRONG PASSWORD! Go back and try again."
    else:
        session_token = str(uuid.uuid4())
        user.session_token = session_token
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for("index")))
        response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")
        return response


@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))

    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if guess == user.secret_number:
        message = "CONGRATULATIONS!!! THE SECRET NUMBER IS {0}".format(str(guess))

        new_secret = random.randint(1, 30)

        user.secret_number = new_secret

        db.add(user)
        db.commit()

    elif guess > user.secret_number:
        message = "Your guess is not correct... try something smaller."
    elif guess < user.secret_number:
        message = "Your guess is not correct... try something bigger."

    return render_template("result.html", message=message)


@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index"))


@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if request.method == "GET":
        if user:
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")
        old_password = request.form.get("old-password")
        new_password = request.form.get("new_password")

        if old_password and new_password:
            hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()

            if hashed_old_password == user.password:
                user.password = hashed_new_password
            else:
                return "Wrong (old) password! Go back and try again."

        user.name = name
        user.email = email

        db.add(user)
        db.commit()

        return redirect(url_for("profile"))


@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token, deleted=False).first()

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
        user.deleted = True
        db.delete(user)
        db.commit()

        return redirect(url_for("index"))


@app.route("/users", methods=["GET"])
def all_users():
    users = db.query(User).filter_by(deleted=False).all()

    return render_template("users.html", users=users)


@app.route("/user/<user_id>", methods=["GET"])
def user_details(user_id):
    user = db.query(User).get(int(user_id))

    return render_template("user_details.html", user=user)


if __name__ == "__main__":
    app.run()

