#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# GET / heroes
@app.route("/heroes", methods=["GET"])
def get_heroes():
    heroes = Hero.query.all()
    heroes_data = [
        {"id": hero.id, "name": hero.name, "super_name": hero.super_name}
        for hero in heroes
    ]
    # heroes_data = [hero.to_dict() for hero in heroes]

    return jsonify(heroes_data), 200


@app.route("/heroes/<int:id>", methods=["GET"])
def get_hero_by_id(id):
    hero = Hero.query.filter(Hero.id == id).first()
    if not hero:
        return jsonify({"error": "Hero not found"}), 404

    hero_data = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": [
            {
                "id": hp.id,
                "hero_id": hp.hero_id,
                "power_id": hp.power_id,
                "strength": hp.strength,
                "power": {
                    "id": hp.power.id,
                    "name": hp.power.name,
                    "description": hp.power.description,
                },
            }
            for hp in hero.hero_powers
        ],
    }
    return jsonify(hero_data), 200


@app.route("/powers", methods=["GET"])
def get_powers():
    powers = Power.query.all()
    powers_data = [
        {"id": power.id, "name": power.name, "description": power.description}
        for power in powers
    ]
    return jsonify(powers_data)


@app.route("/powers/<int:id>", methods=["GET"])
def get_power_by_id(id):
    # power = Power.query.get(id)
    power = Power.query.filter(Power.id == id).first()
    if not power:
        return jsonify({"error": "Power not found"}), 404

    power_data = {"id": power.id, "name": power.name, "description": power.description}
    return jsonify(power_data)


@app.route("/hero_powers", methods=["POST"])
def create_hero_powers():
    data = request.json
    required_fields = ["strength", "power_id", "hero_id"]

    if not all(field in data for field in required_fields):
        return jsonify({"errors": ["validation errors"]}), 400

    hero = Hero.query.filter(data["hero_id"])
    power = Power.query.filter(data["power_id"])

    if not hero or not power:
        return jsonify({"errors": ["validation errors"]}), 404

    try:
        hero_power = HeroPower(
            strength=data["strength"],
            hero_id=data["hero_id"],
            power_id=data["power_id"],
        )
        db.session.add(hero_power)
        db.session.commit()

        return jsonify(
            {
                "id": hero_power.id,
                "hero_id": hero_power.hero_id,
                "power_id": hero_power.power_id,
                "strength": hero_power.strength,
                "hero": {
                    "id": hero.id,
                    "name": hero.name,
                    "super_name": hero.super_name,
                },
                "power": {
                    "id": power.id,
                    "name": power.name,
                    "description": power.description,
                },
            }
        ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


# POST /hero_powers
# @app.route("/hero_powers", methods=["POST"])
# def assign_power_to_hero():
#     data = request.get_json()
#     try:
#         hero_power = HeroPower(
#             strength=data["strength"],
#             hero_id=data["hero_id"],
#             power_id=data["power_id"],
#         )
#         db.session.add(hero_power)
#         db.session.commit()

#         hero = Hero.query.get(hero_power.hero_id)
#         return jsonify(hero.to_dict()), 201
#     except Exception as e:
#         return jsonify({"errors": [str(e)]}), 400


@app.route("/powers/<int:id>", methods=["PATCH"])
def update_power(id):
    power = Power.query.filter(Power.id == id).first()
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.json
    if "description" not in data:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        power.description = data["description"]
        db.session.commit()
        return jsonify(
            {"id": power.id, "name": power.name, "description": power.description}
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
