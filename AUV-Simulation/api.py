import json

from fastapi import FastAPI
from fastapi.responses import FileResponse

from simulation.simulator import Simulator


app = FastAPI()


# =========================
# LOAD CONFIGURATION
# =========================

with open("config.json", "r") as file:
    config = json.load(file)


# =========================
# CREATE SIMULATOR
# =========================

simulator = Simulator(config)

# Start the SAR search pattern
simulator.setup_sar_search()


# =========================
# STORE AUV ROUTE
# =========================

auv_route = []


# =========================
# HOME PAGE
# =========================

@app.get("/")
def home():
    return FileResponse("dashboard.html")


# =========================
# SIMULATION DATA
# =========================

@app.get("/data")
def get_data():

    data = simulator.step(10)

    position = data["navigation"]["position"]

    auv_route.append({
        "latitude": position["latitude"],
        "longitude": position["longitude"]
    })

    return data


# =========================
# AUV ROUTE
# =========================

@app.get("/route")
def get_route():

    return {
        "route": auv_route
    }


# =========================
# SAR SEARCH PATTERN
# =========================

@app.get("/sar-search")
def get_sar_search():

    search_pattern = simulator.sar.generate_search_pattern(
        simulator.sar.target_latitude,
        simulator.sar.target_longitude
    )

    return {
        "search_pattern": search_pattern
    }