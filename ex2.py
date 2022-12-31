from copy import deepcopy
from collections import deque
import time
from itertools import combinations
import itertools
import ast

ids = ["111111111", "222222222"]


def bfs_distance(map, start):
    # Set up the distance and visited arrays
    distance = [[-1 for _ in row] for row in map]
    visited = [[False for _ in row] for row in map]

    # Initialize the queue and add the starting cell
    queue = deque([start])
    distance[start[0]][start[1]] = 0
    visited[start[0]][start[1]] = True

    # Set up the directions for traversing the map
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    # Loop until the queue is empty
    while queue:
        # Pop the first cell from the queue
        x, y = queue.popleft()

        # Check the neighbors of the current cell
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if nx >= 0 and ny >= 0 and nx < len(map) and ny < len(map[0]) and (
                    map[nx][ny] == 'G' or map[nx][ny] == 'P') and not visited[nx][ny]:
                # Add the neighbor to the queue and set its distance
                queue.append((nx, ny))
                distance[nx][ny] = distance[x][y] + 1
                visited[nx][ny] = True

    # Return the distance array
    return distance


def get_valid_locations(map, current_loc):
    x, y = current_loc
    max_x = len(map)
    max_y = len(map[0])
    locations = []
    for i in [-1, 1]:
        if (0 <= x + i) and ((x + i) < max_x) and ((map[x + i][y] == 'P') or (map[x + i][y] == 'G')):
            locations.append((x + i, y))
        if (0 <= y + i) and (y + i < max_y) and ((map[x][y + i] == 'P') or (map[x][y + i] == 'G')):
            locations.append((x, y + i))
    return locations


class OptimalTaxiAgent:
    def __init__(self, initial):
        self.initial = initial
        initial_copy = deepcopy(initial)
        self.board = initial_copy.pop('map')

        self.col = len(self.board[0])
        self.row = len(self.board)
        self.valid_moves_dict = self.valid_moves_dict_builder()
        self.utility_dict = {}

        self.turns_to_go = initial['turns to go']
        self.states = {}
        self.state_actions = {}
        self.new_states = {}
        self.probabilities = {}

        self.possible_states = self.all_possible_states()
        self.value_iteration()

    def probability(self, state, new_state):
        prob = 1
        passengers_dict_state = state["passengers"]
        for passenger in new_state["passengers"]:
            temp = 0
            # if the passenger haven't changed their destination
            dest1 = new_state["passengers"][passenger]['destination']
            dest2 = passengers_dict_state[passenger]['destination']
            if dest1 == dest2:
                temp += 1 - state['passengers'][passenger]['prob_change_goal']
                # and their destination is part of their possible goals
                if new_state['passengers'][passenger]['destination'] in new_state['passengers'][passenger] \
                        ['possible_goals']:
                    temp += state['passengers'][passenger]['prob_change_goal'] / (len(new_state['passengers'][passenger] \
                                                                                          ['possible_goals']))
            else:
                temp += state['passengers'][passenger]['prob_change_goal'] / (len(new_state['passengers'][passenger] \
                                                                                      ['possible_goals']))
            prob *= temp
        return prob

    def taxi_action(self, state):
        passengers_dict = state["passengers"]
        passengers_set = state["passengers"].keys()
        taxis_dict = state["taxis"]
        taxis_set = state["taxis"].keys()
        taxis_actions = {}
        for taxi in taxis_set:
            taxis_actions[taxi] = []
            taxi_location = state["taxis"][taxi]["location"]

            if taxis_dict[taxi]["fuel"] >= 1:
                valid_moves = self.valid_moves_dict[taxi_location]
                for location in valid_moves:
                    taxis_actions[taxi].append(("move", taxi, location))

            for passenger in passengers_set:
                passenger_location = passengers_dict[passenger]["location"]
                if taxi_location == passengers_dict[passenger]["destination"] and passenger_location == taxi:
                    taxis_actions[taxi].append(("drop off", taxi, passenger))
                if passenger_location == taxi_location and taxis_dict[taxi]["capacity"] > 0 and passenger_location != \
                        passengers_dict[passenger]["destination"]:
                    taxis_actions[taxi].append(("pick up", taxi, passenger))

            x, y = taxi_location
            if self.board[x][y] == "G":
                taxis_actions[taxi].append(("refuel", taxi))
            taxis_actions[taxi].append(("wait", taxi))

        actions = list(itertools.product(*taxis_actions.values()))
        possible_actions = []

        if len(state['taxis']) > 1:
            for act in actions:
                loc_in_act = set(loc[2] if loc[0] == "move" else state["taxis"][loc[1]]["location"] for loc in act)
                if len(loc_in_act) == len(state['taxis'].keys()):
                    possible_actions.append(act)
            return tuple(possible_actions)

        actions.append('reset')
        actions.append('terminate')
        return actions

    def state_and_action(self, state, action):

        if action[0] == 'terminate':
            return "terminate"

        if action[0] == 'reset':
            reset_state = deepcopy(self.initial)
            del reset_state['turns to go']
            return reset_state

        new_state = deepcopy(state)
        for act in action:
            if act[0] == "move":
                new_state["taxis"][act[1]]["location"] = act[2]
                new_state["taxis"][act[1]]["fuel"] -= 1
            else:
                if act[0] == "pick up":
                    new_state["taxis"][act[1]]["capacity"] -= 1
                    new_state["passengers"][act[2]]["location"] = act[1]
                else:
                    if act[0] == "drop off":
                        new_state["taxis"][act[1]]["capacity"] += 1
                        new_state["passengers"][act[2]]["location"] = state["taxis"][act[1]]["location"]
                    else:
                        if act[0] == "refuel":
                            new_state["taxis"][act[1]]["fuel"] = self.initial["taxis"][act[1]]["fuel"]
        return new_state

    def all_possible_states(self):
        initial = deepcopy(self.initial)
        del initial['turns to go']
        all_possible_states = {self.turns_to_go: [str(initial)]}

        for t in reversed(range(self.turns_to_go)):
            all_possible_states[t] = set()

            # go through every state in every level of the tree
            for state in all_possible_states[t + 1]:
                if state not in self.states.keys():
                    self.states[state] = set()

                    if state == 'terminate':
                        continue

                    dict_flag = False

                    # get all the action we can do with the given state
                    if state not in self.state_actions.keys():
                        current = ast.literal_eval(state)
                        dict_flag = True
                        possible_actions = self.taxi_action(current)
                        self.state_actions[state] = possible_actions
                    else:
                        possible_actions = self.state_actions[state]

                    # use the possible actions to get to new states
                    for action in possible_actions:
                        if (state, action) not in self.new_states.keys():
                            if not dict_flag:
                                current = ast.literal_eval(state)
                            new_state = self.state_and_action(current, action)
                            if new_state == 'terminate':
                                continue
                            self.new_states[(state, action)] = [str(new_state)]
                            all_possible_states[t].add(str(new_state))
                            self.states[state].add(str(new_state))

                            if (state, str(new_state)) not in self.probabilities.keys():
                                if action == 'reset':
                                    self.probabilities[(state, str(new_state))] = 1
                                else:
                                    self.probabilities[(state, str(new_state))] = self.probability(current, new_state)

                            # more possible states that we haven't had in the dict and we can discover earlier

                            if action != 'reset' and action != 'terminate':
                                dest = {}

                                for passenger in new_state["passengers"]:
                                    dest[passenger] = new_state["passengers"][passenger]['possible_goals']

                                # will create every combination of a state with the possible destinations of the passengers
                                comb = list(itertools.product(*dest.values()))
                                for c in comb:
                                    possible_state = new_state
                                    for i, passenger in enumerate(dest.keys()):
                                        possible_state["passengers"][passenger]['destination'] = c[i]

                                    # will calculate the probability
                                    if (state, str(possible_state)) not in self.probabilities.keys():
                                        self.probabilities[(state, str(possible_state))] = self.probability(current,
                                                                                                            possible_state)

                                    all_possible_states[t].add(str(possible_state))
                                    self.new_states[(state, action)].append(str(possible_state))
                                    self.states[state].add(str(possible_state))

                    # if the state and action combination already exists, we unite
                    else:
                        all_possible_states[t] = all_possible_states[t].union(set(self.new_states[state, action]))
                        self.states[state] = self.states[state].union(set(self.new_states[(state, action)]))
                # if the state exists in our states dict
                else:
                    all_possible_states[t] = all_possible_states[t].union(self.states[state])

        return all_possible_states

    '''

    def initialize_utility(self):
        utility_dict = {}
        for i in range(self.row):
            for j in range(self.col):
                utility_dict[(i, j)] = 0

        return utility_dict
'''

    def valid_moves_dict_builder(self):
        board_i = len(self.board)
        board_j = len(self.board[0])
        valid_moves_dict = {}
        for i in range(board_i):
            for j in range(board_j):
                location = (i, j)
                valid_moves = get_valid_locations(self.board, (i, j))
                valid_moves_dict[location] = valid_moves

        return valid_moves_dict

    def reward(self, action):
        drop_off_count = 0
        refuel_count = 0
        if action == 'reset':
            return -50
        for i, taxi in enumerate(self.initial["taxis"].keys()):
            if action[i][0] == "refuel":
                refuel_count -= 10
            if action[i][0] == 'drop off':
                drop_off_count += 100

        return refuel_count + drop_off_count

    def calculate_u(self, state, action, turn):

        # here we do the sum of the possible states s'
        next_states = set(self.new_states[(state, action)])
        u_value = 0
        for next in next_states:
            prob = self.probabilities[(state, next)]
            prev_u = (self.utility_dict[(next, turn - 1)][0])
            u_value += prob * prev_u

        return u_value

    def value_iteration(self):

        error = 0
        possible_states = list(self.possible_states)
        for turn in range(self.turns_to_go + 1):

            for state in self.possible_states[turn]:
                max_reward = -500000
                if turn == 0:

                    self.utility_dict[(state, turn)] = (0, 'done')
                else:
                    valid_actions = self.state_actions[state]
                    for action in valid_actions:
                        if action == 'terminate':
                            continue
                        max_u = 0
                        max_u = self.calculate_u(state, action, turn)

                        r_s = self.reward(action)
                        if max_u + r_s > max_reward:
                            max_reward = max_u + r_s
                            max_action = action

                    self.utility_dict[(state, turn)] = (max_reward, max_action)

    def act(self, state):

        new_state = deepcopy(state)
        del new_state["turns to go"]
       # print(self.utility_dict[(str(new_state), state["turns to go"])][0])
        return self.utility_dict[(str(new_state), state["turns to go"])][1]


class TaxiAgent:
    def __init__(self, initial):
        self.initial = initial
        initial_copy = deepcopy(initial)
        self.board = initial_copy.pop('map')
        self.distance_dict = self.distance_dict_builder(self.board)
        self.valid_moves_dict = self.valid_moves_dict_builder()

    def distance_dict_builder(self, map):

        distance_dict = {}
        col = len(map[0])
        row = len(map)
        for i in range(row):
            for j in range(col):
                distance_dict[(i, j)] = bfs_distance(map, (i, j))

        return distance_dict

    def valid_moves_dict_builder(self):
        board_i = len(self.board)
        board_j = len(self.board[0])
        valid_moves_dict = {}
        for i in range(board_i):
            for j in range(board_j):
                location = (i, j)
                valid_moves = get_valid_locations(self.board, (i, j))
                valid_moves_dict[location] = valid_moves

        return valid_moves_dict

    def translate_state(self, state):
        additional_info = {
            "taxis": {},
            "passengers": {}
        }
        taxis_set = state["taxis"].keys()
        for taxi in taxis_set:
            additional_info["taxis"][taxi] = {}
            passengers_in_taxi = [passenger for passenger in state["passengers"].keys() if
                                  state["passengers"][passenger]["location"] == taxi]
            additional_info['taxis'][taxi]["passengers in taxi"] = passengers_in_taxi

        for passenger in state["passengers"].keys():
            additional_info["passengers"][passenger] = {}
            status = "waiting"
            location = state["passengers"][passenger]["location"]
            destination = state['passengers'][passenger]['destination']
            for taxi in taxis_set:
                if location == taxi:
                    status = "picked"
            if location == destination:
                status = "drooped"
            additional_info["passengers"][passenger]["status"] = status

        return additional_info

    def taxi_action(self, state, taxi, additional_info):
        passengers_dict = state["passengers"]
        passengers_set = state["passengers"].keys()
        taxis_dict = state["taxis"]
        # drop off
        taxi_location = state["taxis"][taxi]["location"]
        for passenger in passengers_set:
            if taxi == passengers_dict[passenger]["location"] and taxi_location == passengers_dict[passenger][
                "destination"]:
                return "drop off", taxi, passenger

        # pick up
        # check if I have place for passenger
        if taxis_dict[taxi]["capacity"] > 0:
            # check if I have passenger to pick
            for passenger in passengers_set:
                if taxi_location == passengers_dict[passenger]["location"] and passengers_dict[passenger]["location"] != \
                        passengers_dict[passenger]["destination"]:
                    return "pick up", taxi, passenger

        # refuel
        # start with simple check
        x, y = taxi_location
        # can be faster is I put a boolean in dict
        if self.board[x][y] == 'G':
            return "refuel", taxi

        # move

        locations = self.valid_moves_dict[taxi_location]
        # check if I have someone to droop
        if len(additional_info["taxis"][taxi]["passengers in taxi"]) > 0:
            # I create two lists one is locations includes the valid locations, and one is for possible destinations
            # includes passengers destination, and I pick the best move option

            optionals_destinations = []
            best_move = None
            shortest = float('inf')
            for passenger in additional_info["taxis"][taxi]["passengers in taxi"]:
                optionals_destinations.append(passengers_dict[passenger]["destination"])

            for location in locations:
                x, y = location
                path_size = self.distance_dict[taxi_location][x][y]
                if path_size < shortest:
                    shortest = path_size
                    best_move = location

            return "move", taxi, best_move

        else:
            optionals_destinations = []
            best_move = None
            shortest = float('inf')
            for passenger in passengers_dict:
                if passengers_dict[passenger]["location"] != passengers_dict[passenger]["destination"] and \
                        additional_info["passengers"][passenger]["status"] == "waiting":
                    optionals_destinations.append(passengers_dict[passenger]["location"])

            for location in locations:
                x, y = location
                path_size = self.distance_dict[taxi_location][x][y]

                if path_size < shortest:
                    shortest = path_size
                    best_move = location

            return "move", taxi, best_move

    def act(self, state):

        additional_info = self.translate_state(state)
        actions = {taxi: ("wait", taxi) for taxi in state["taxis"] if taxi != "taxi 1"}
        taxi_chosen = "taxi 1"
        action_taxi = self.taxi_action(state, taxi_chosen, additional_info)
        actions["taxi 1"] = action_taxi
        actions_values = tuple(actions.values())
        for passenger in state["passengers"].keys():
            if additional_info["passengers"][passenger]["status"] == "drooped":
                return "terminate"

        return actions_values
