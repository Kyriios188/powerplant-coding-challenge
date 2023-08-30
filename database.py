from dataclasses import dataclass
import sys


@dataclass
class PowerPlant:
    name: str
    type: str
    efficiency: float
    pmin: int
    pmax: int

    contribution: float | None

    def __init__(self, powerplant_data: dict):
        self.name = powerplant_data['name']
        self.type = powerplant_data['type']
        self.efficiency = powerplant_data['efficiency']
        self.pmin = powerplant_data['pmin']
        self.pmax = powerplant_data['pmax']

        self.contribution = None

    def __str__(self):
        return self.name


@dataclass
class Fuels:
    gas: float  # gas(euro/MWh): 13.4,
    kerosine: float  # kerosine(euro/MWh): 50.8,
    co2: int  # co2(euro/ton): 20,
    wind: int  # wind(%): 60

    def __init__(self, fuel_data: dict):
        self.gas = fuel_data['gas(euro/MWh)']
        self.kerosine = fuel_data['kerosine(euro/MWh)']
        self.co2 = fuel_data['co2(euro/ton)']
        self.wind = fuel_data['wind(%)']


class ProductionPlanData:
    powerplants: list[PowerPlant] = []
    load: int
    fuels: Fuels

    # Map between the powerplant type and the Fuel attribute
    fuel_map: dict = {
        "turbojet": "kerosine",
        "windturbine": "wind",
        "gasfired": "gas"
    }

    def __init__(self, plan_data):
        self.load = plan_data['load']
        self.fuels = Fuels(fuel_data=plan_data['fuels'])

        self.powerplants = []
        for powerplant_data in plan_data['powerplants']:
            self.powerplants.append(PowerPlant(powerplant_data=powerplant_data))
        self.compute_plan()

    def get_max_power_output(self, plant: PowerPlant):
        if plant.type == "windturbine":
            return self.fuels.wind * plant.pmax / 100
        else:
            return plant.pmax

    def compute_highest_contribution(self, plant: PowerPlant, load: float) -> float | None:
        """Computes the most power a powerplant can offer to achieve a given load."""

        max_output: float = self.get_max_power_output(plant)

        # If the load is too small, return None since the plant will surpass the load which is not allowed
        if load < plant.pmin:
            return None
        # If the plant's pmax is superior to the load, achieve exactly the load
        elif max_output > load:
            return load
        # If the load is too high, achieve as much as possible
        else:
            return max_output

    def get_cost_for_powerplant(self, plant: PowerPlant, power: float) -> float:
        """
        Get the cost of power for a powerplant (in €) i.e. "What does it cost if the plant produces x amount?"
        """

        fuel_type: str = self.fuel_map[plant.type]
        if fuel_type == "wind":
            return 0
        else:
            # If you ask a plant to product 460MWh with an efficiency of 0.53,
            # it will use an equivalent in fuel of 460MWh / 0.53 = 867.9MWh
            return getattr(self.fuels, fuel_type) * power / plant.efficiency if plant.efficiency != 0 else sys.maxsize

    def export_plan(self) -> list[dict]:
        """Desired output is a list of 2 key-value pairs"""

        output: list[dict] = []
        for plant in self.powerplants:
            output.append({
                "name": plant.name,
                "p": plant.contribution or 0.0  # contribution can be None
            })
        return output

    def compute_plan(self) -> None:
        """
        Iterates over the list of PowerPlants to find the cheapest combination of power they can contribute.
        Updates each PowerPlant's contribution value.
        """

        # The first plant is the cheapest, last is the most expensive
        sorted_plants = sorted(
            self.powerplants, key=lambda powerplant: self.get_cost_for_powerplant(powerplant, 1)
        )

        # list of plants that can be reevaluated, the first plant being the cheapest
        can_be_reevaluated: list[PowerPlant] = []
        # list of plants that have not contributed yet
        can_contribute: list[PowerPlant] = sorted_plants
        remaining_load: float = self.load

        while remaining_load != 0 and can_contribute != []:
            cheapest_plant: PowerPlant = can_contribute[0]
            plant_contribution: float | None = self.compute_highest_contribution(cheapest_plant, remaining_load)

            if plant_contribution:
                remaining_load -= plant_contribution
                cheapest_plant.contribution = plant_contribution
                can_be_reevaluated.insert(0, cheapest_plant)
            else:
                # Cancel the contribution of the previous plant, substract its pmin from the remaining_load
                # and compute the highest contribution of the previous plant again
                to_be_reevaluated: PowerPlant = can_be_reevaluated[0]
                remaining_load = remaining_load + to_be_reevaluated.contribution - cheapest_plant.pmin

                # The plant we just assigned cannot be reevaluated, but it has contributed
                cheapest_plant.contribution = cheapest_plant.pmin

                # The previous plant will be reevaluated

                to_be_reevaluated.contribution = None
                can_contribute.insert(0, to_be_reevaluated)
                # If this happens multiple times, evaluate another plant instead of this one again
                can_be_reevaluated.remove(to_be_reevaluated)

            can_contribute.remove(cheapest_plant)
