import json

from simulation.simulator import Simulator


with open("config.json", "r") as file:
    config = json.load(file)


simulator = Simulator(config)

simulator.run()