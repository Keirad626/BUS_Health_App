from flask import Blueprint, render_template, request, redirect, url_for, session

app = Blueprint("app", __name__)

#just creating some temp users here
users = {
    "ElderlyPerson": {"password": "abc123", "role": "Elder"},
    "Carer": {"password": "1234", "role": "Carer"},
    "Family": {"password": "4567", "role": "Son"},
    "Admin": {"password": "7890", "role": "Admin"}
}

#make it so that family members can book an appointment, cancel an appointment, view upcoming appointments etc

@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("app.login"))

    return render_template(
        "index.html",
        username = session["username"],
        role=session["role"]
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            session["username"] = username
            session["role"] = users[username]["role"]
            return redirect(url_for("app.index"))
        else:
            return render_template("login.html", error="Invalid login details")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("app.login"))