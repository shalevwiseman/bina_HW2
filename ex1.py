import json
import sys

import search
import random
import math
import itertools
from copy import deepcopy

ids = ["318269248", "205671266"]


class TaxiProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        initial_copy = deepcopy(initial)
        initial_dist = dict()
        passengers = set()
        self.board = initial_copy.pop("map")
        self.gas_stations = [(r, c) for r in range(len(self.board)) for c in range(len(self.board[0])) if
                             self.board[r][c] == 'G']
        self.total_capacity = 0
        self.passengers = initial_copy["passengers"]
        self.taxis = initial_copy["taxis"]
        self.taxis_num = len(self.taxis)
        for taxi in self.taxis:
            fuel = initial_copy["taxis"][taxi]["fuel"]
            capacity = initial_copy["taxis"][taxi]["capacity"]
            self.total_capacity += capacity
            initial_copy["taxis"][taxi]["passengers"] = []
            initial_copy["taxis"][taxi]["current capacity"] = capacity
            initial_copy["taxis"][taxi]["current fuel status"] = fuel

        for passenger in initial_copy["passengers"]:
            passengers.add(passenger)
            location = initial_copy["passengers"][passenger]["location"]
            destination = initial_copy["passengers"][passenger]["destination"]
            initial_copy["passengers"][passenger]["status"] = "waiting"
            initial_dist.update({passenger: (abs(destination[0] - location[0]) + abs(destination[1] - location[1]))})
            initial_copy["passengers"][passenger]["dist to dest"] = self.calc_manhattan_distance(location, destination)

        self.init_passengers_dit = initial_dist

        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        search.Problem.__init__(self, str(initial_copy))

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        actions = dict()
        if state == None:
            return tuple(actions)

        new_state = eval(state)
        passengers_dict = new_state["passengers"]
        taxis_dict = new_state["taxis"]

        for taxi in taxis_dict:

            actions[taxi] = []
            current_fuel_capacity = taxis_dict[taxi]["current fuel status"]
            taxi_location = taxis_dict[taxi]["location"]
            fuel = taxis_dict[taxi]["current fuel status"]

            # move action
            locations = self.get_valis_locations(taxi_location)

            if self.taxis_num == 1:
                if current_fuel_capacity != 0: # and not self.is_it_dead_end(taxi_location, new_state, fuel, taxi):
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
        return tuple(actions_prod)

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        new_state = eval(state)

        action_list = list(action)
        num_of_actions = len(action_list)
        taxis_dict = new_state["taxis"]
        passengers_dict = new_state["passengers"]

        # No update
        """ move update:
                1) taxi fuel capacity
                2)  taxi location
                3)  if I have passengers i will update their locations
            pick up update:
                1) add the passenger name to the relevant taxi
                2) current capacity down by 1
            drop off update:
                1) remove the passenger name to the relevant taxi
                2) current capacity up by 1
            refuel update:
                1) up to the max fuel capacity 
                """
        for i in range(num_of_actions):
            action_name = action_list[i][0]
            taxi_name = action_list[i][1]
            if action_name == "wait":
                continue

            elif action_name == "move":
                location = action_list[i][2]
                taxis_dict[taxi_name]["current fuel status"] -= 1
                taxis_dict[taxi_name]["location"] = location

                for passenger in new_state["taxis"][taxi_name]["passengers"]:
                    passengers_dict[passenger]["location"] = location

            elif action_name == "pick up":
                passenger_name = action_list[i][2]
                passengers_dict[passenger_name]["status"] = "picked"
                taxis_dict[taxi_name]["passengers"].append(passenger_name)
                taxis_dict[taxi_name]["current capacity"] -= 1

            elif action_name == "drop off":
                passenger = action_list[i][2]
                taxis_dict[taxi_name]["passengers"].remove(passenger)
                taxis_dict[taxi_name]["current capacity"] += 1
                passengers_dict[passenger]["status"] = "dropped"

            elif action_name == "refuel":
                taxis_dict[taxi_name]["current fuel status"] = new_state["taxis"][taxi_name]["fuel"]

            else:
                continue

        return str(new_state)

    def goal_test(self, state):

        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        if state == None:
            return False

        new_state = eval(state)
        passengers_dict = new_state["passengers"]
        taxis_dict = new_state["taxis"]

        for passenger in passengers_dict:
            if passengers_dict[passenger]["location"] != passengers_dict[passenger]["destination"]:
                return False
        for taxi in taxis_dict:
            if len(taxis_dict[taxi]["passengers"]) != 0:
                return False

        return True

    def h(self, node):

        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

        state = eval(node.state)
        unpicked, picked_but_undelivered, delivered_passenger = self.unpicked_delivered_inside(state)

        total_capacity = 0
        sum_dist_to_dest = 0
        taxis_dict = state["taxis"]
        passengers_dict = state["passengers"]
        taxis = dict()
        min_total_dist_to_unpicked = 0

        for taxi in taxis_dict:
            total_capacity += taxis_dict[taxi]["current capacity"]
            max_temp_dist = 0
            min_temp_dist = float('inf')
            dist_dest_and_picked = dict()
            if len(taxis_dict[taxi]["passengers"]) > 0:
                for passenger in taxis_dict[taxi]["passengers"]:

                    current_dist_to_dest = self.dist_to_dest(state, passenger)
                    # for every passenger we add the dist to his dest
                    dist_dest_and_picked.update({passenger: current_dist_to_dest})
                    # calc the max\min dest btw every passenger in the taxi
                    max_temp_dist = max(max_temp_dist, current_dist_to_dest)
                    min_temp_dist = min(min_temp_dist, self.dist_to_dest(state, passenger))
                # sum the all maxes dist
                sum_dist_to_dest += max_temp_dist
            min_dist_to_unpicked_passenger = float('inf')

            for passenger in unpicked:
                # check the min dist from every taxi to unpicked passenger
                min_dist_to_unpicked_passenger = min(min_dist_to_unpicked_passenger,
                                                     self.dist_taxi_to_unpicked_passenger(state, taxi, passenger))
            temp_dist = float('inf')
            for picked_passenger in dist_dest_and_picked:
                for passenger in unpicked:
                    temp_dist = min(temp_dist, self.dist_btw_dest_and_pickup(state, picked_passenger, passenger))

                # for every passenger in the taxi we have the drop&pick dist
                dist_dest_and_picked[picked_passenger] += temp_dist
            # for every taxi we want the min of (dist to dest + pick up)
            if dist_dest_and_picked.values():
                min_dist_plus_dest = min(dist_dest_and_picked.values())
            else:
                min_dist_plus_dest = 0
            taxis[taxi] = {"max passenger dist": max_temp_dist, "min passenger dist": min_temp_dist,
                           "min dist to unpicked": min_dist_to_unpicked_passenger,
                           "drop&pick dist": min_dist_plus_dest}

        if total_capacity == 0:
            min_total_dist_to_unpicked = float('inf')
            for taxi in taxis:
                min_total_dist_to_unpicked = min(min_total_dist_to_unpicked, taxis[taxi]["drop&pick dist"])

        score = sum_dist_to_dest + min_total_dist_to_unpicked


        return score

    def h_1(self, node):

        """
                This is a simple heuristic
                """
        state = eval(node.state)
        passenger_list = []
        unpicked_passenger = []
        picked_but_undelivered = []
        taxis_list = []
        for passenger in state["passengers"]:
            passenger_list.append(passenger)

        for taxi in state["taxis"]:
            taxis_list.append(taxi)
            for passenger in passenger_list:
                for i in range(len(state["taxis"][taxi]["passengers"])):
                    if state["taxis"][taxi]["passengers"][i] == passenger:
                        picked_but_undelivered.append(passenger)

        unpicked_passenger = passenger_list
        for passenger in passenger_list:
            if (passenger in picked_but_undelivered) or state["passengers"][passenger]["location"] == \
                    state["passengers"][passenger]["destination"]:
                unpicked_passenger.remove(passenger)

        res = (len(unpicked_passenger) * 2) + ((len(picked_but_undelivered)) / len(taxis_list))
        return res

    def h_2(self, node):

        """
        This is a slightly more sophisticated Manhattan heuristic
        """
        state = eval(node.state)

        passenger_list = []
        unpicked_passenger = []
        picked_but_undelivered = []
        taxis_list = []
        for passenger in state["passengers"]:
            passenger_list.append(passenger)

        for taxi in state["taxis"]:
            taxis_list.append(taxi)
            for passenger in passenger_list:
                for i in range(len(state["taxis"][taxi]["passengers"])):
                    if state["taxis"][taxi]["passengers"][i] == passenger:
                        picked_but_undelivered.append(passenger)

        unpicked_passenger = passenger_list
        for passenger in passenger_list:
            if (passenger in picked_but_undelivered) or state["passengers"][passenger]["location"] == \
                    state["passengers"][passenger]["destination"]:
                unpicked_passenger.remove(passenger)

        t = 0
        d = 0
        for passenger in unpicked_passenger:
            d += self.init_passengers_dit[passenger]

        for passenger in picked_but_undelivered:
            t += abs(
                state["passengers"][passenger]["location"][0] - state["passengers"][passenger]["destination"][0]) + abs(
                state["passengers"][passenger]["location"][1] - state["passengers"][passenger]["destination"][1])

        res = (d + t) / (len(state["taxis"]))
        return res

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

    def h_3(self, node):

        new_dict = eval(node.state)
        passengers = new_dict["passengers"]
        taxis = new_dict["taxis"]
        unpicked_sum = 0
        picked_sum = 0
        unpicked = 0
        picked = 0
        for passenger in passengers:
            current_location = passengers[passenger]["location"]
            dest = passengers[passenger]["destination"]
            if passengers[passenger]["status"] == "waiting":
                unpicked += 1
                unpicked_sum += self.calc_manhattan_distance(current_location, dest)

            if passengers[passenger]["status"] == "picked":
                picked += 1
                picked_sum += self.calc_manhattan_distance(current_location, dest)

        tax_num = len(taxis)
        t_cap = 0
        for taxi in taxis:
            t_cap += taxis[taxi]["capacity"]
        h1 = (unpicked * 2 + picked) / tax_num
        h2 = unpicked_sum + picked_sum
        if t_cap > 0:
            h2 = h2 / t_cap
        res = max(h1, h2)
        return res

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

    def dist_to_dest(self, state, passenger):
        """

        :param state:
        :return: the distance to the passenger destination
        """
        dist = abs(state["passengers"][passenger]["location"][0] - state["passengers"][passenger]["destination"][0]) + \
               abs(state["passengers"][passenger]["location"][1] - state["passengers"][passenger]["destination"][1])
        return dist

    def dist_taxi_to_unpicked_passenger(self, state, taxi, passenger):
        dist = abs(state["taxis"][taxi]["location"][0] - state["passengers"][passenger]["location"][0]) + \
               abs(state["taxis"][taxi]["location"][1] - state["passengers"][passenger]["location"][1])
        return dist

    def dist_btw_dest_and_pickup(self, state, passenger_to_drop, passenger_to_pick):
        dist = abs(state["passengers"][passenger_to_pick]["location"][0] -
                   state["passengers"][passenger_to_drop]["destination"][0]) + \
               abs(state["passengers"][passenger_to_pick]["location"][1] -
                   state["passengers"][passenger_to_drop]["destination"][1])
        return dist

    def unpicked_delivered_inside(self, state):

        passenger_list = []
        delivered_passenger = []
        delivered = 0
        picked_but_undelivered = []

        for passenger in state["passengers"]:
            passenger_list.append(passenger)
            if state["passengers"][passenger]["location"] == state["passengers"][passenger]["destination"]:
                delivered = delivered + 1
                delivered_passenger.append(passenger)

        for taxi in state["taxis"]:
            for passenger in passenger_list:
                for i in range(len(state["taxis"][taxi]["passengers"])):
                    if state["taxis"][taxi]["passengers"][i] == passenger:
                        picked_but_undelivered.append(passenger)
                        if passenger in delivered_passenger:
                            delivered_passenger.remove(passenger)

        unpicked = passenger_list
        for passenger in passenger_list:
            if (passenger in picked_but_undelivered) or state["passengers"][passenger]["location"] == \
                    state["passengers"][passenger]["destination"]:
                unpicked.remove(passenger)

        return unpicked, picked_but_undelivered, delivered_passenger

    def dist_to_gas_station(self, taxi_location):
        row = taxi_location[0]
        col = taxi_location[1]
        map = self.board
        if map[row][col] == 'G':
            return 0
        gas_stations = [(r, c) for r in range(len(map)) for c in
                        range(len(map[0])) if map[r][c] == 'G']
        closest_station = min(gas_stations, key=lambda x: self.calc_manhattan_distance(taxi_location, x))
        return self.calc_manhattan_distance(taxi_location, closest_station)

    def calc_manhattan_distance(self, loc1, loc2):
        return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])

    def is_it_dead_end(self, taxi_location, state, fuel_status, taxi):

        nearest_station = min(self.gas_stations, key=lambda x: self.calc_manhattan_distance(x, taxi_location))
        dist_to_nearest_station = self.calc_manhattan_distance(nearest_station, taxi_location)
        nearest_pick_and_dest = sys.maxsize
        length = len(state["taxis"][taxi]["passengers"])
        nearest_dest = sys.maxsize
        #picked, delivered, unpicked = self.unpicked_delivered_inside(state)
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


def create_taxi_problem(game):
    return TaxiProblem(game)
