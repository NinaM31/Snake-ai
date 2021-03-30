from collections import deque
from Utility import Node
from Algorithm import Algorithm


class BFS(Algorithm):
    def __init__(self, grid):
        super().__init__(grid)

    def run_algorithm(self, snake):
        # start clean
        self.frontier = deque([])
        self.explored_set = []
        self.path = []

        initialstate, goalstate = self.get_initstate_and_goalstate(snake)

        # open list
        self.frontier.append(initialstate)

        # while we have states in open list
        while len(self.frontier) > 0:
            shallowest_node = self.frontier.popleft()  # FIFO queue
            self.explored_set.append(shallowest_node)

            # get neighbors
            neighbors = self.get_neighbors(shallowest_node)

            # for each neighbor
            for neighbor in neighbors:
                # check if path inside snake, outside boundary or already visited
                if self.inside_body(snake, neighbor) or self.outside_boundary(neighbor):
                    self.explored_set.append(neighbor)
                    continue  # skip this path

                if neighbor not in self.frontier and neighbor not in self.explored_set:
                    neighbor.parent = shallowest_node  # mark parent
                    self.explored_set.append(neighbor)  # mark visited
                    # add to frontier to explore its kids next cycle
                    self.frontier.append(neighbor)

                    # check if goal state
                    if neighbor.equal(goalstate):
                        # return path
                        return self.get_path(neighbor)
        return None
