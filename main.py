from flask import Flask, request, render_template, make_response
import random


app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    secret_number = request.cookies.get("secret_number")
    response = make_response(render_template("index.html"))
    if secret_number is None:
        secret_number = random.randint(0, 30)
        response.set_cookie("secret_number", str(secret_number))
    return response


@app.route("/result", methods=["POST"])
def result():
    guess = int(request.form.get("guess"))
    secret_number = int(request.cookies.get("secret_number"))

    if guess == secret_number:
        message = "CORRECT! THE SECRET NUMBER IS {0}".format(str(secret_number))
        response = make_response(render_template("result.html", message=message))
        response.set_cookie("secret_number", str(random.randint(0, 30)))
        return response
    elif guess > secret_number:
        message = "Your guess is not correct... try something smaller."
        return render_template("result.html", message=message)
    elif guess < secret_number:
        message = "Your guess is not correct... try something bigger."
        return render_template("result.html", message=message)


if __name__ == "__main__":
    app.run()

