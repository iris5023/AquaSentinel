from flask import Flask, jsonify, request
from flask_cors import CORS

from pollution_module import PollutionSensor


app = Flask(__name__)
CORS(app)


sensor = PollutionSensor(
    seed=None,
    water_type="auto",
    auto_dive=True
)


@app.route("/api/pollution", methods=["GET"])
def get_pollution_reading():

    depth_param = request.args.get("depth")

    if depth_param is not None:

        try:
            sensor.set_depth(float(depth_param))

        except ValueError:
            return jsonify({
                "error": "depth must be a number"
            }), 400

    reading = sensor.read()

    return jsonify(reading)


@app.route("/api/pollution/health", methods=["GET"])
def health_check():

    return jsonify({
        "status": "ok",
        "module": "pollution"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )