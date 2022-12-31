from copy import deepcopy
from collections import deque

ids = ["111111111", "222222222"]


def bfs_paths(map, start):
    # Set up the distance and visited arrays
    distance = [[-1 for _ in row] for row in map]
    visited = [[False for _ in row] for row in map]
    # Set up the predecessor array to store the path
    predecessor = [[(-1, -1) for _ in row] for row in map]

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
            if nx >= 0 and ny >= 0 and nx < len(map) and ny < len(map[0]) and (map[nx][ny] == 'G' or map[nx][ny] == 'P') and not visited[nx][ny]:
                # Add the neighbor to the queue, set its distance, and set its predecessor
                queue.append((nx, ny))
                distance[nx][ny] = distance[x][y] + 1
                predecessor[nx][ny] = (x, y)
                visited[nx][ny] = True

    # Set up the paths dictionary
    paths = {}

    # Loop through all cells on the map
    for i in range(len(map)):
        for j in range(len(map[0])):
            # Skip the starting cell
            if (i, j) == start:
                continue

            # Set up the path list
            path = []

            # Follow the predecessor chain to reconstruct the path
            x, y = (i, j)
            while predecessor[x][y] != (-1, -1):
                path.append((x, y))
                x, y = predecessor[x][y]

            # Reverse the path list to get the path from start to end
            path = path[::-1]

            # Add the path and distance to the dictionary
            paths[(i, j)] = {'path': path, 'distance': len(path)}
            if map[i][j] == 'I':
                paths[(i, j)]['distance'] = float('inf')

    # Return the paths dictionary
    return paths

def get_min_dist_point(optional_destinations, start, paths_dict, valid_moves):
    if len(valid_moves) == 1:
        return valid_moves[0]
    global_min = float('inf')
    global_min_point = None
    current_dest = None

    for valid_move in valid_moves:
        local_min = float('inf')
        local_min_point = None
        for destination in optional_destinations:
            if destination == valid_move:
                return valid_move
            current_dist = paths_dict[valid_move][destination]["distance"]
            if current_dist < local_min:
                local_min = current_dist
                local_min_point = destination
        if local_min < global_min:
            global_min = local_min
            current_dest = local_min_point
            global_min_point = valid_move
    return global_min_point

"""map = [['P', 'P', 'P', 'P', 'P'],
           ['P', 'I', 'P', 'G', 'P'],
           ['P', 'P', 'I', 'P', 'P'],
           ['P', 'P', 'P', 'I', 'P']]
           optional_dest = [(3,1),(2,4)]
           valid_moves = [(0,0),(0,2)]
           global_min = 4
           global_point = (0,0)
           local_min = 4
           local_point = (3,1)
           current_dist = 4
           current_dest = (3,1)
           """


"""def get_min_dist_point(optional_points, start, paths_dict, valid_locations):
    min_distance = float('inf')
    min_point = None
    best_move = None
    min_dist_to_best = float('inf')
    for location in valid_locations:
        for point in optional_points:
            if point in paths_dict[location].keys():
                current_dist = paths_dict[location][point]["distance"]
                if current_dist != 0 and current_dist < min_distance:
                    min_distance = paths_dict[location][point]["distance"]
                    min_point = point
            if min_distance < min_dist_to_best:
                min_dist_to_best = min_distance
                best_move = location
    return best_move"""


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
        self.paths_dict, self.gas_station_dict = self.distance_dict_builder(self.board)
        self.valid_moves_dict = self.valid_moves_dict_builder()
        self.initial_info = {}
        for taxi in initial_copy["taxis"].keys():
            self.initial_info[taxi] = {}
            self.initial_info[taxi]["initial fuel"] = initial_copy["taxis"][taxi]["fuel"]
            self.initial_info[taxi]["initial capacity"] = initial_copy["taxis"][taxi]["capacity"]
        self.score = 0
        self.best_taxi, self.best_passenger, self.best_path = self.pick_taxi_and_passenger(initial_copy)
        self.current_dest = initial_copy["passengers"][self.best_passenger]["destination"]




    def distance_dict_builder(self, map):

        distance_dict = {}
        gas_station_dict = {}
        col = len(map[0])
        row = len(map)
        for i in range(row):
            for j in range(col):
                distance_dict[(i, j)] = bfs_paths(map, (i, j))
                distance_dict[(i, j)][(i, j)] = {}
                distance_dict[(i, j)][(i, j)]["path"] = []
                distance_dict[(i, j)][(i, j)]["distance"] = 0


                if map[i][j] == 'G':
                    gas_station_dict[(i, j)] = distance_dict[(i, j)]

        return distance_dict, gas_station_dict

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

    def shortest_path_with_gas(self, path, paths_dict, gas_stations, fuel):
        """
        @param
        input: path as a list, paths_dict, list of gas_stations, current amount of fuel
        output: the shortest path with same start point and destination who also cross a gas station,
        the distance to the gas station,
        the distance from the gas station to the destination
        """
        min_dist_to_gas = float('inf')
        min_point = None
        best_gas_station = None
        min_point_idx = -1
        gas_station = None
        start = path[0]
        destination = path[-1]
        for i in range(len(path)):
            min_dist_local = float('inf')
            closet_gas_station = None
            if path[i] in gas_stations:
                return path, paths_dict[path[0]][path[i]]["distance"], paths_dict[path[i]][path[-1]]["distance"]
            for gas_station in gas_stations:
                if paths_dict[path[i]][gas_station]['distance'] < min_dist_local:
                    min_dist_local = paths_dict[path[i]][gas_station]['distance']
                    closet_gas_station = gas_station
            if min_dist_local < min_dist_to_gas:
                min_dist_to_gas = min_dist_local
                min_point = path[i]
                best_gas_station = closet_gas_station
                min_point_idx = i
        path_to_gas = paths_dict[min_point][best_gas_station]["path"]
        gas_to_path_dist = paths_dict[best_gas_station][min_point]["distance"]
        gas_to_path_path = paths_dict[best_gas_station][min_point]["path"]
        complete_path = paths_dict[min_point][destination]["path"]
        complete_path_dist = paths_dict[min_point][destination]["distance"]
        gas_to_dest_dist = paths_dict[best_gas_station][destination]["distance"]
        gas_to_dest_path = paths_dict[best_gas_station][destination]["path"]
        total_distance_to_nearest_gas_station = len(path[:min_point_idx + 1]) + len(path_to_gas)
        if gas_to_dest_dist < (gas_to_path_dist + complete_path_dist):
            new_path = path[:min_point_idx + 1] + path_to_gas + paths_dict[best_gas_station][path[-1]]["path"]
            distance_from_gas_station_to_dest = len(paths_dict[best_gas_station][path[-1]]["path"])
        else:
            new_path = path[:min_point_idx + 1] + path_to_gas + paths_dict[gas_station][min_point]["path"] + path[min_point_idx + 1:]
            distance_from_gas_station_to_dest = len(paths_dict[gas_station][min_point]["path"] + path[min_point_idx + 1:])
        return new_path, total_distance_to_nearest_gas_station, distance_from_gas_station_to_dest

    def check_fuel(self, fuel, path, paths_dict, gas_stations):
        # if you have enough fuel foe pick + drop, return the path
        if fuel >= len(path):
            return path
        # else, get new path that cross gas station
        new_path, total_distance_to_nearest_gas_station, distance_from_gas_station_to_dest = self.shortest_path_with_gas(path, paths_dict, gas_stations, fuel)
        # if you don't have enough fuel to the gas station return None, it's mean that you can't get forward
        if fuel < total_distance_to_nearest_gas_station or fuel < distance_from_gas_station_to_dest:
            return None
        # if you have enough gas
        return new_path



    def pick_taxi_and_passenger(self, state):
        map = self.board
        taxis_set = state["taxis"].keys()
        taxis_dict = state["taxis"]
        passengers_set = state["passengers"].keys()
        passengers_dict = state["passengers"]
        taxis_paths_dict = {}
        """ iterate every taxi, and check what is the shortest dist to pick someone and drop him  
        """
        best_dist_taxi_to_passenger = float('inf')
        best_taxi = None
        best_passenger = None
        best_passenger_loc = None
        best_passenger_dest = None
        best_path = None
        for taxi in taxis_set:
            fuel = taxis_dict[taxi]["fuel"]
            taxi_location = taxis_dict[taxi]["location"]
            other_taxis = [other_taxi for other_taxi in taxis_set if other_taxi != taxi]
            for other_taxi in other_taxis:
                x, y = taxis_dict[other_taxi]["location"]
                map[x][y] = 'I'
            taxi_path, gas_stations = self.distance_dict_builder(map)
            taxis_paths_dict[taxi] = taxi_path
            min_dist_per_taxi = float('inf')
            best_passenger_per_taxi = None
            best_passenger_loc_per_taxi = None
            best_passenger_dest_per_taxi = None

            """
            for every passenger check 
            """
            for passenger in passengers_set:

                passenger_location = passengers_dict[passenger]["location"]
                passenger_destination = passengers_dict[passenger]["destination"]
                dist_to_passenger = taxi_path[taxi_location][passenger_location]['distance']
                dist_to_destination = taxi_path[passenger_location][passenger_destination]['distance']
                total_path = taxi_path[taxi_location][passenger_location]['path'] + taxi_path[passenger_location][passenger_destination]["path"]
                total_dist = dist_to_passenger + dist_to_destination

                if self.check_fuel(fuel, total_path, taxi_path, gas_stations) is not None:
                    total_dist = total_dist
                    if total_dist < min_dist_per_taxi:
                        min_dist_per_taxi = total_dist
                        best_passenger_per_taxi = passenger
                        best_passenger_loc_per_taxi = passenger_location
                        best_passenger_dest_per_taxi = passenger_destination
            # check if this passenger is the nearest
            if min_dist_per_taxi < best_dist_taxi_to_passenger:
                best_dist_taxi_to_passenger = min_dist_per_taxi
                best_passenger = best_passenger_per_taxi
                best_taxi = taxi
                best_passenger_loc = best_passenger_loc_per_taxi
                best_passenger_dest = best_passenger_dest_per_taxi
            if best_passenger_loc == None or best_passenger_dest == None:
                continue
            best_path = taxi_path[taxi_location][best_passenger_loc]["path"] + taxi_path[best_passenger_loc][best_passenger_dest]["path"]

        print(best_taxi, best_passenger, best_path)
        return best_taxi, best_passenger, best_path





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
                if taxi_location == passengers_dict[passenger]["location"]:
                    if passengers_dict[passenger]["location"] == passengers_dict[passenger]["destination"]:
                        return "wait", taxi
                    else:
                        return "pick up", taxi, passenger

        # refuel
        # start with simple check
        x, y = taxi_location
        # can be faster is I put a boolean in dict
        if self.board[x][y] == 'G' and state["taxis"][taxi]["fuel"] < self.initial_info[taxi]["initial fuel"]:
            return "refuel", taxi

        # move
        if len(additional_info["taxis"][taxi]["passengers in taxi"]) > 0:
            if state["passengers"][self.best_passenger]["destination"] == self.current_dest:
                if len(self.best_path) > 0:
                    best_move = self.best_path.pop(0)
                    return "move", taxi, best_move
                else:
                    return "wait", taxi
            else:
                self.current_dest = state["passengers"][self.best_passenger]["destination"]
                print(self.current_dest)

                passenger_location = state["passengers"][self.best_passenger]["location"]
                passenger_dest = self.current_dest
                self.best_path = self.paths_dict[taxi_location][self.current_dest]["path"]
                print(self.best_path)
                if len(self.best_path) > 0:
                    best_move = self.best_path.pop(0)
                    return "move", taxi, best_move
                else:
                    return "wait", taxi
        else:
            if len(self.best_path) > 0:
                best_move = self.best_path.pop(0)
                return "move", taxi, best_move
            else:
                return "wait", taxi

    def act(self, state):

        additional_info = self.translate_state(state)
        actions = {taxi: ("wait", taxi) for taxi in state["taxis"] if taxi != self.best_taxi}

        action_taxi = self.taxi_action(state, self.best_taxi, additional_info)
        actions[self.best_taxi] = action_taxi
        actions_values = tuple(actions.values())
        if state["taxis"][self.best_taxi]['fuel'] == 0:
            self.score -= 50
            return "reset"
        for passenger in state["passengers"].keys():
            if self.score > 0:

                return "terminate"
        if action_taxi[0] == "drop off":
            self.score += 100


        if action_taxi[0] == "refuel":
            self.score -= 10

        print(actions_values)
        return actions_values

