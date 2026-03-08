import os

from flask import Flask, render_template, jsonify, request
from faker import Faker
import random

app = Flask(__name__)
fake = Faker()


def generate_profile():
    """Generate a single fake profile."""
    gender = random.choice(["male", "female"])
    first_name = fake.first_name_male() if gender == "male" else fake.first_name_female()
    last_name = fake.last_name()
    avatar_seed = f"{first_name}{last_name}".lower().replace(" ", "")
    return {
        "name": f"{first_name} {last_name}",
        "email": fake.email(),
        "phone": fake.phone_number(),
        "address": fake.address().replace("\n", ", "),
        "city": fake.city(),
        "country": fake.country(),
        "date_of_birth": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%B %d, %Y"),
        "job": fake.job(),
        "company": fake.company(),
        "username": fake.user_name(),
        "website": fake.url(),
        "bio": fake.text(max_nb_chars=120),
        "gender": gender.capitalize(),
        "avatar": f"https://api.dicebear.com/7.x/personas/svg?seed={avatar_seed}",
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate")
def api_generate():
    """Generate one or more fake profiles."""
    count = request.args.get("count", 1, type=int)
    count = max(1, min(count, 10))
    profiles = [generate_profile() for _ in range(count)]
    return jsonify(profiles)


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)
