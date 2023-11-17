# powerplant-coding-challenge

## Installation

The algorithm has been developed in Python, using Flask to launch a web server that receives the calculation requests. A web page has also been developed to access the API and test.

To test the application, download the code:


```bash

git clone git@github.com:jlb-visual/powerplant-coding-challenge.git

```

Install the necessary packages

```bash

$ pip install -r requirements.txt

```

And launch the server:

```bash

$ python app.py

```

Then you can open the browser's main page for port 8888 (localhost:8888) and start testing. To do this select a combination of values an press the submit button.

## Algorithm

The program writes the results obtained in the intermediate steps of the calculation

The algorithm implemented to determine the optimal load combination of the plants has been developed taking as a starting point the most intuitively obvious case, which is the one in which all the wind plants are active. In this case, the power provided by the wind turbines is subtracted from the total power required and the remaining power is attempted to be covered by the gas and kerosene plants, starting with those that have a lower cost.

The algorithm is iterative, having as a reference value the value of the power to be covered and iterating over the list of plants ordered by production cost from lowest to highest. CO2 rights can be included in this cost

Thus, for each plant, to consider:

1. If the total power to be covered is higher than the minimum power value (Pmin) of the plant considered:
    * If the total to be covered is higher than the maximum power (Pmax) of the plant under consideration, select the plant with the maximum power value, and subtract this amount from the total power to cover and consider the next plant.
    * If the amount of remaining power is lowe than the maximum value of the plant under consideration, select the plant with a power value equal to the remaining power and terminate the algorithm.

2. If the power to be covered is lower than the minimum value of the plant under consideration, mark that plant as turned off and move on to the next one in the list.

On top of this algorithm, we have taken into account the possibility that, in some cases it may be more economical to close a wind plant in order to reach the total power with a gas plant with a lower cost than the last one activated.

To explore this possibility, the program calculates all the combinations of having wind plants on and off and for each case calculates the production cost with the previous algorithm. Of all these cases, the lowest cost option is chosen.


## Limitations

The format of the solution does not allow indicating the existence of problems (for example: we cannot reach the required power) or errors in the input data. The algorithm in this case returns an error message and not a solution

This is a quick implementation of the proposed problem. It has been developed, considering two premises:

* That the number of wind plants is low, since the power calculation must be carried out 2 to the power of N times to find the most appropriate combination, with N being the number of wind plants.

* Gas and kerosene plants have the characteristic that the larger the size of the plant, the higher the value of P Mean and the lower the cost. For this reason, the solution will always have a number of plants working at maximum power and one that will be the one with the highest cost, covering the difference between the total produced and that required. If this premise were not met, it is possible that the final solution would be more complex and the implemented algorithm would not be valid.

The solution in both cases would be the implementation of a simplex method for solving linear programming problems.

