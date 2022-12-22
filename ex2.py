import random
import math
import itertools
from copy import deepcopy
from collections import deque

ids = ["111111111", "222222222"]


class OptimalTaxiAgent:
    def __init__(self, initial):
        self.initial = initial

    def act(self, state):
        raise NotImplemented


class TaxiAgent:
    def __init__(self, initial):
        self.initial = initial
        initial_copy = deepcopy(initial)

        self.turns_init = initial_copy["turns to go"]
        self.board = initial_copy.pop('map')
        self.distance_dict = self.distance_dict_builder(self.board)
        self.valid_moves_dict = self.valid_moves_dict_builder(self.board)


    def distance_dict_builder(self, map):
        distance_dict = {}
        col = len(map[0])
        row = len(map)
        for i in range(row):
            for j in range(col):
                distance_dict[(i, j)] = bfs_distance(map, (i, j))

        return distance_dict

    def valid_moves_dict_builder(self, map):
        board_i = len(map)
        board_j = len(map[0])
        valid_moves_dict = {'location': {}}
        for i in range(board_i):
            for j in range(board_j):
                location = (i, j)
                valid_moves = self.get_valid_locations((i, j))
                valid_moves_dict['location'][location] = {'valid moves': valid_moves}

        return valid_moves_dict

    def get_valid_locations(self, current_loc):
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

    def taxi_action(self, state, taxi):

        # drop off
        taxi_location = state[taxi]['location']
        for passenger in state["passengers"]:
            if taxi == state['passengers'][passenger]['location']:
                if taxi_location == state['passengers'][passenger]['destination']:
                    return "drop off", taxi, passenger

        # pick up
        if state['taxis'][taxi]['capacity'] > 0:
            for passenger in state["passengers"]:
                if taxi_location == state['passengers'][passenger]['location'] and state['passengers'][passenger] \
                        ['destination'] != state['passengers'][passenger]['location']:
                    return "pick up", taxi,

        # refuel
        if state['taxis'][taxi]['location'] == 'G':
            return "refuel", taxi

        # move
        


    def act(self, state):
        new_state = translate_state(state)
        chosen_taxi = new_state['taxis']['taxi 1']
        action_taxi = self.taxi_action(new_state, chosen_taxi)

        return action_taxi.values()


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


def translate_state(state):
    state_copy = state.copy()
    new_state = {'taxis': {}, 'passengers': {}}

    for taxi in state_copy['taxis']:
        new_state['taxis'][taxi] = {}
        location = state_copy['taxis'][taxi]['location']
        fuel = state_copy['taxis'][taxi]['fuel']
        capacity = state_copy['taxis'][taxi]['capacity']

        new_state['taxis'][taxi] = {'location': location, 'fuel': fuel, 'capacity': capacity}
        # check if to enter the passengers in the taxi here or not

    for passenger in state_copy['passengers']:
        new_state['passengers'][passenger] = {}
        location = state_copy['passengers'][passenger]['location']
        destination = state_copy['passengers'][passenger]['destination']
        possible_goals = [goal for goal in state_copy['passengers'][passenger]['possible_goals']]

        new_state['passengers'][passenger] = {'location': location, 'destination': destination,
                                              'possible_goals': possible_goals}

    return new_state
