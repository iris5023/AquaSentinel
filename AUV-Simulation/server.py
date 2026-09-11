from flask import Flask, jsonify, send_from_directory
import json
import os

from simulation.simulator import Simulator


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


with open(
    os.path.join(BASE_DIR, "config.json"),
    "r"
) as file:

    config = json.load(file)


simulator = Simulator(config)


@app.route("/")
def dashboard():

    return send_from_directory(
        BASE_DIR,
        "dashboard.html"
    )


@app.route("/AquaSentinel_Underwater.glb")
def auv_model():

    return send_from_directory(
        BASE_DIR,
        "AquaSentinel_Underwater.glb"
    )


@app.route("/data")
def get_data():

    data = simulator.step(2)

    return jsonify(data)


@app.route("/route")
def get_route():

    return jsonify({
        "route":
        simulator.navigation.waypoints
    })


@app.route("/sar-search")
def sar_search():

    pattern = simulator.sar.generate_search_pattern(
        simulator.sar.target_latitude,
        simulator.sar.target_longitude
    )

    return jsonify({
        "search_pattern": pattern
    })


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )