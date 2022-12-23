from copy import deepcopy
from collections import deque

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

    def act(self, state):
        raise NotImplemented


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
            "passengers" : {}
        }
        taxis_set = state["taxis"].keys()
        for taxi in taxis_set:
            additional_info["taxis"][taxi] = {}
            passengers_in_taxi = [passenger for passenger in state["passengers"].keys() if state["passengers"][passenger]["location"] == taxi]
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
            if taxi == passengers_dict[passenger]["location"] and taxi_location == passengers_dict[passenger]["destination"]:
                return "drop off", taxi, passenger

        # pick up
        # check if I have place for passenger
        if taxis_dict[taxi]["capacity"] > 0:
            # check if I have passenger to pick
            for passenger in passengers_set:
                if taxi_location == passengers_dict[passenger]["location"] and passengers_dict[passenger]["location"] != passengers_dict[passenger]["destination"]:
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

