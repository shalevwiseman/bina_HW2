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

    def distance_dict_builder(self, map):

        distance_dict = {}
        col = len(map[0])
        row = len(map)
        for i in range(row):
            for j in range(col):
                distance_dict[(i, j)] = bfs_distance(map, (i, j))

        return distance_dict






    def act(self, state):
        raise NotImplemented
