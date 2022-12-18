import itertools
import sys
from copy import deepcopy

ids = ["111111111", "222222222"]


def calc_manhattan_distance(loc1, loc2):
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])
def get_valis_locations(self, current_loc):
    x, y = current_loc
    max_x = len(self.board)
    max_y = len(self.board[0])
    locations = []
    for i in [-1, 1]:
        if (0 <= x + i) and ((x + i) < max_x) and ((self.board[x + i][y] == 'P') or (self.board[x + i][y] == 'G')):
            locations.append((x + i, y))
        if (0 <= y + i) and (y + i < max_y) and ((self.board[x][y + i] == 'P') or (self.board[x][y + i] == 'G')):
            locations.append((x, y + i))
    return locations
def is_it_dead_end(self, taxi_location, state, fuel_status, taxi):

    nearest_station = min(self.gas_stations, key=lambda x: calc_manhattan_distance(x, taxi_location))
    dist_to_nearest_station = calc_manhattan_distance(nearest_station, taxi_location)
    nearest_pick_and_dest = sys.maxsize
    length = len(state["taxis"][taxi]["passengers"])
    nearest_dest = sys.maxsize

    taxis_dict = state["taxis"]
    passengers_dict = state["passengers"]

    if length > 0:
        for passenger in taxis_dict[taxi]["passengers"]:
            passenger_dest = passengers_dict[passenger]["destination"]
            nearest_dest = min(nearest_dest, self.calc_manhattan_distance(taxi_location, passenger_dest))
    else:
        for passenger in passengers_dict:
            if passengers_dict[passenger]["status"] == "waiting":
                dist_to_pick = self.calc_manhattan_distance(self.passengers[passenger]['location'], taxi_location)
                dist_to_dest = self.passengers[passenger]['dist to dest']
                nearest_pick_and_dest = min(nearest_dest, (dist_to_pick + dist_to_dest))

    if fuel_status < min(dist_to_nearest_station, nearest_dest, nearest_pick_and_dest):
        return True

    return False


class OptimalTaxiAgent:
    def __init__(self, initial):
        initial_copy = deepcopy(initial)
        initial_dist = dict()
        passengers = set()
        self.board = initial_copy.pop("map")
        self.gas_stations = [(r, c) for r in range(len(self.board)) for c in range(len(self.board[0])) if
                             self.board[r][c] == 'G']
        self.total_capacity = 0
        self.optimal = initial_copy["optimal"]
        self.passengers = initial_copy["passengers"]
        self.taxis = initial_copy["taxis"]
        self.taxis_num = len(self.taxis)
        self.initial = initial_copy
        initial_copy["reward"] = 0

        for taxi in self.taxis:
            fuel = initial_copy["taxis"][taxi]["fuel"]
            capacity = initial_copy["taxis"][taxi]["capacity"]
            self.total_capacity += capacity
            initial_copy["taxis"][taxi]["passengers"] = []
            initial_copy["taxis"][taxi]["current capacity"] = capacity
            initial_copy["taxis"][taxi]["current fuel status"] = fuel
            initial_copy["taxis"][taxi]["initial location"] = initial_copy["taxis"][taxi]["location"]

        for passenger in initial_copy["passengers"]:
            passengers.add(passenger)
            location = initial_copy["passengers"][passenger]["location"]
            destination = initial_copy["passengers"][passenger]["destination"]
            num_of_options = len(initial_copy["passengers"][passenger]["possible_goals"])
            initial_copy["passengers"][passenger]["num of options"] = num_of_options
            initial_copy["passengers"][passenger]["initial location"] = location
            initial_copy["passengers"][passenger]["status"] = "waiting"
            initial_dist.update({passenger: (abs(destination[0] - location[0]) + abs(destination[1] - location[1]))})
            initial_copy["passengers"][passenger]["dist to dest"] = calc_manhattan_distance(location, destination)

    def act(self, state):
        actions = dict()
        if state == None:
            return tuple(actions)

        new_state = eval(state)
        passengers_dict = new_state["passengers"]
        taxis_dict = new_state["taxis"]

        # reset



        for taxi in taxis_dict:

            actions[taxi] = []
            current_fuel_capacity = taxis_dict[taxi]["current fuel status"]
            taxi_location = taxis_dict[taxi]["location"]
            fuel = taxis_dict[taxi]["current fuel status"]

            # move action
            locations = get_valis_locations(taxi_location)

            if self.taxis_num == 1:
                if current_fuel_capacity != 0:  # and not self.is_it_dead_end(taxi_location, new_state, fuel, taxi):
                    for location in locations:
                        actions[taxi].append(("move", taxi, location))
            else:
                if current_fuel_capacity != 0 and not self.is_it_dead_end(taxi_location, new_state, fuel, taxi):
                    for location in locations:
                        actions[taxi].append(("move", taxi, location))
            #
            # pick up
            for passenger in passengers_dict:
                if taxi_location == passengers_dict[passenger]["location"] and \
                        taxis_dict[taxi]["current capacity"] > 0 and passengers_dict[passenger]["status"] == "waiting":
                    actions[taxi].append(("pick up", taxi, passenger))
            # drop off
            for passenger in taxis_dict[taxi]["passengers"]:

                if taxi_location == passengers_dict[passenger]["destination"]:
                    actions[taxi].append(("drop off", taxi, passenger))
            # refuel
            if self.board[taxi_location[0]][taxi_location[1]] == 'G':
                actions[taxi].append(("refuel", taxi))

            # wait
            if current_fuel_capacity == 0:
                actions[taxi].append(("wait", taxi))

        actions_prod = [action for action in itertools.product(*actions.values())]

        invalid_actions = set()
        for action in actions_prod:  # remove options where two taxis pick up the same person
            for x in range(len(action)):
                for y in range(x + 1, len(action)):
                    if action[x][0] == 'pick up' and action[y][0] == 'pick up' and action[x][1] != action[y][1] and \
                            action[x][2] == action[y][2] \
                            or (action[x][0] == 'move' and action[y][0] == 'move ' and action[x][1] != action[y][1] and
                                action[x][2][0] == action[y][2][0] and action[x][2][1] == action[y][2][1]):
                        invalid_actions.add(action)

        actions_prod = [action for action in actions_prod if action not in invalid_actions]
        actions_prod.append(("reset"))
        actions_prod.append(("terminate"))
        return tuple(actions_prod)
    #

    def transition(self, state, action, next_state):


        """
        action_name = action[0]
        taxi = action[1]
        next_location = next_state["taxis"][taxi]["location"]
        curren_fuel = state["taxis"][taxi]["current fuel status"]
        next_fuel = next_state["taxis"][taxi]["current fuel status"]
        #move
        if action_name == "move":
            location = action[2]
            if not location == next_location:
                return 0
            if not curren_fuel == next_fuel + 1:
                return 0
        """
        prob = []
        passengers_dict = self.passengers

        for passenger in passengers_dict:
            current_dest = state["passengers"][passenger]["destination"]
            next_dest = next_state["passengers"][passenger]["destination"]
            prob_to_change = passengers_dict[passenger]["prob_change_goal"]
            if current_dest == next_dest:
                prob.append(1 - prob_to_change)
            else:
                prob.append((prob_to_change)/(state["passengers"][passenger]["num of options"]))

        res = 1
        for i in range(len(prob)):
            res = res * prob[i]



        return res




class TaxiAgent:
    def __init__(self, initial):
        self.initial = initial

    def act(self, state):
        raise NotImplemented
