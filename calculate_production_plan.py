from pprint import pprint
from itertools import product


def calculate_optimal_power_plant_usage(solution, fuel_powerplants):
    """
    Calculate a combination of fuel power plant production given 
    certain combination of wind parks connected

    Inputs:
    solution: a dictionary with the wind powerplants options and a field named 
    'target_laod' with the load figure that must be met and another field 
    'accumulated_load' with the power provided by the sum of the 
    fuel_powerplants: a dictionary with the information of the fuel_powerplants

    fuel_powerplants is ordered by unit cost
    """
    debug = True
    if solution['target_load'] < solution['accumulated_load']:
        # The sum of the powerplants exceeds the target
        if debug: print("Capacity exceeded")
        return False, None, None, None

    remaining_load = solution['target_load'] - solution['accumulated_load']
    accumulated_cost = solution['cost']

    ret_dicts = []

    for plant in fuel_powerplants:
        # create output dictionary item
        plant_data = {}
        plant_data['name'] =plant['name']

        if plant['pmin'] < remaining_load and remaining_load > 0:
            if plant['pmax'] > remaining_load:
                if debug: print("added", plant_data['name'])
                plant_data['p'] = round(remaining_load, 2)
                accumulated_cost += plant_data['p']*plant['unitary_cost']
                remaining_load = 0
            else:
                if debug: print("added", plant_data['name'])
                plant_data['p'] = plant['pmax']
                accumulated_cost += plant_data['p']*plant['unitary_cost']
                remaining_load -= plant['pmax']
        else:
            plant_data['p'] = 0

        ret_dicts.append(plant_data)

    if remaining_load > 0.0001:
        if debug: print("Solution not found; remaining_load:", remaining_load)
        return False, None, None, None 

    return True, accumulated_cost, solution['target_load'], ret_dicts 



def check_input_data_format(input_data):
    """
    Check if input data is a dictionary and has the right format

    Format expected is as follows:
    {
      "load": 480,
      "fuels":
      {
        "gas(euro/MWh)": 13.4,
        "kerosine(euro/MWh)": 50.8,
        "co2(euro/ton)": 20,
        "wind(%)": 60
      },
      "powerplants": [
        {
          "name": "gasfiredbig1",
          "type": "gasfired",
          "efficiency": 0.53,
          "pmin": 100,
          "pmax": 460
        },...]
    }

    Returns 

    success: True if the format is correct, False otherwise
    error_message: Literal indicating the error detected
    """

    if not isinstance(input_data, dict):
        return False, "[ERROR] input data is not a dictionary"

    if not all(key in input_data for key in ['load', 'fuels', 'powerplants']):
        return False, "[ERROR]Error in input data, 'power', 'fuels', 'powerplants' must be the main dictionary keys"

    if not all(key in input_data['fuels'] for key in ["gas(euro/MWh)","kerosine(euro/MWh)","co2(euro/ton)","wind(%)"]):
        return False, '[ERROR] Error in input data, "fuels" info expected variables: "gas(euro/MWh)","kerosine(euro/MWh)","co2(euro/ton)" and "wind(%)")'

    if not (isinstance(input_data['powerplants'], list) and all(isinstance(item, dict) for item in input_data['powerplants'])):
        return False, '[ERROR] Error in input data, "powerplants" variable must be a list'

    for item in input_data['powerplants']:
        if not all(key in item for key in ["name", "type", "efficiency", "pmin", "pmax"]):
            return False, '[ERROR] Error in input data, "powerplants" info expected variables: "name", "type", "efficiency", "pmin", "pmax"'
    return True, "Input is correct"

def calculate_production_plan(input_data):
    """
    Calculate a production plan given the requirements 


    Considering that we only have a single variable to minimize which is cost in Euros,
    and that this is purely a linear function, the obvious result will be composed 
    by choosing the plants starting by that with the lowest cost and so on until the target
    production is reached. 

    The function also takes into consideration the possibility of shutting down a certain number
    of wind farms if by doing so the target production is reached with a lower cost combination´

    If an error is found, instead of a solution an error message is returned

    """

    # Verify that input_data has the right directory structure 

    success,  err_msg = check_input_data_format(input_data)

    if not success:
        return False, err_msg

    # get variables from input dictionary

    load = float(input_data["load"])

    gas_cost = float(input_data["fuels"]["gas(euro/MWh)"])
    kerosine_cost = float(input_data["fuels"]["kerosine(euro/MWh)"])
    co2_cost = float(input_data["fuels"]["co2(euro/ton)"])
    wind = float(input_data["fuels"][f"wind(%)"])

    # add unitary cost to each powerplant

    powerplants = input_data["powerplants"]

    for p in powerplants: 
        p['turned_on'] = False
        if p["type"] == "gasfired":
            p["unitary_cost"] = gas_cost / float(p["efficiency"])
            # add co2 costs
            p["unitary_cost"] += 0.2 * co2_cost

        elif p["type"] == "turbojet":
            p["unitary_cost"] = kerosine_cost / float(p["efficiency"])
            # add co2 costs
            p["unitary_cost"] += 0.2 * co2_cost

        else:
            # cost of wind is 0
            p["unitary_cost"] = 0

            # also for our calculations, pmax is limited by the percentage of wind
            p['pmax'] = p['pmax'] * wind /100

    # sort powerplants by unitary costs

    powerplants.sort(key=lambda x: x['unitary_cost'])

    print("Unitary costs:")
    pprint(powerplants)
    print("---------------------------------------------------------------------------")

    wind_powerplants = [p for p in powerplants if p['type'] == "windturbine"]

    fuel_powerplants = [p for p in powerplants if p['type'] != "windturbine"]

    #print("wind_powerplants:", wind_powerplants)

    """
    Take into account the possibility of shutting down a certain 
    wind park if we need to reach the minimum power to turn on a 
    gas plant that may give a cheaper result

    All the possible combinations of wind parks are considered
    """
    # Generate all combinations of 'on_or_off' values for the wind powerplants
    combinations = list(product([True, False], repeat=len(wind_powerplants)))

    # print(combinations)

    """
    Use this list to generate all the combinations of wind powerplants 
    Generate the combinations in the output format expected that is:
    [
    {
        "name": "windpark1",
        "p": 90.0
    },...
    ]
    
    Since there are going to be multiple options that need to be calculated,
    additional cost and load fields are added to a solution record
    """

    wind_options = []
    for c in combinations:
        solution = {"cost":0.0, "accumulated_load":0.0, "target_load":load, "plant_data": []}
        for i in range(len(wind_powerplants)):
            plant_data = {}
            plant_data['name'] = wind_powerplants[i]['name']
            plant_data['p'] = round(wind_powerplants[i]['pmax'] * wind /100 * c[i], 2)
            solution['accumulated_load'] += plant_data['p']
            solution['plant_data'].append(plant_data)

        wind_options.append(solution)


    """
    So far solutions is list of wind powerplants combinations with all the different options of ON or OFF
    
    Now the full solution is calculated for each case
    """
    print("Wind options:")
    pprint(wind_options)
    print("---------------------------------------------------------------------------")

    solutions = []

    for s in wind_options:
        success, cost, accumulated_load, plant_data = calculate_optimal_power_plant_usage(s, fuel_powerplants)
        if success:
            print("adding s:", s)
            s['cost'] += cost 
            s['accumulated_load'] = accumulated_load
            s['plant_data'] += plant_data
            solutions.append(s)

    solutions.sort(key=lambda x: x['cost'])

    print("Solutions:")
    pprint(solutions)
    print("---------------------------------------------------------------------------")

    if len(solutions) == 0:
        err_msg = "[ERROR] No solution found"
        return False, err_msg

    return True, solutions[0]["plant_data"]
