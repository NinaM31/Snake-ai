from Algorithm import Algorithm
from Snake import Snake
import math
import random
from Utility import Node
from Constants import NO_OF_CELLS, BANNER_HEIGHT, USER_SEED
import numpy as np
random.seed(USER_SEED)


class Population:
    population = 300
    hidden_node = 8

    def __init__(self):
        self.snakes = []
        self.saved_snakes = []

    def _initialpopulation_(self):
        for _ in range(Population.population):
            self.snakes.append(Snake(Population.hidden_node))

    def remove(self, snake):
        self.saved_snakes.append(snake)
        self.snakes.remove(snake)


class GA(Algorithm):
    generation = 30
    mutation_rate = 0.12

    def __init__(self, grid):
        super().__init__(grid)
        self.population = Population()
        self.generation = 0
        self.best_score = 0
        self.best_gen = 0
        self.best_snake = None

    def died(self, snake):
        current_x = snake.body[0].x
        current_y = snake.body[0].y

        if snake.ate_body() or snake.life_time > 80:
            self.population.remove(snake)

        elif not 0 <= current_x < NO_OF_CELLS or not BANNER_HEIGHT <= current_y < NO_OF_CELLS:
            self.population.remove(snake)

    def next_generation(self):
        if self.generation == GA.generation:
            return False

        self.calculateFitness()
        self.get_best_snake()
        self.naturalSelection()
        self.population.saved_snakes = []
        return True

    def done(self):
        return len(self.population.snakes) <= 0

    def get_best_snake(self):
        best_snake = self.population.saved_snakes[0]
        for snake in self.population.saved_snakes:
            if snake.fitness > best_snake.fitness:
                best_snake = snake

        if best_snake.score > self.best_score:
            self.best_score = best_snake.score
            self.best_gen = self.generation
            self.best_snake = best_snake

        return best_snake

    def check_directions(self, snake, directions, inputs):
        if self.outside_boundary(directions) or self.inside_body(snake, directions):
            inputs.append(1)
        else:
            inputs.append(0)

    def run_algorithm(self, snake):
        inputs = []
        fruit = Node(snake.get_fruit().x, snake.get_fruit().y)

        # head direction
        x = snake.body[0].x
        y = snake.body[0].y

        if snake.body[1].x == x:
            # left = Node(x-1, y)
            # right = Node(x+1, y)

            if snake.body[1].y < y:
                # going down
                forward = Node(x, y+1)
                left = Node(x-1, y)
                right = Node(x+1, y)
            else:
                # going up
                forward = Node(x, y-1)
                left = Node(x+1, y)
                right = Node(x-1, y)

        elif snake.body[1].y == y:
            # left = Node(x, y+1)
            # right = Node(x, y-1)

            if snake.body[1].x < x:
                # going right
                forward = Node(x+1, y)
                left = Node(x, y-1)
                right = Node(x, y+1)

            else:
                # going left
                forward = Node(x-1, y)
                left = Node(x, y+1)
                right = Node(x, y-1)

        # look at forward, left and right
        self.check_directions(snake, forward, inputs)
        self.check_directions(snake, left, inputs)
        self.check_directions(snake, right, inputs)

        # suggest closest movment to the apple
        forward_to_apple = self.euclidean_distance(fruit, forward)
        left_to_apple = self.euclidean_distance(fruit, left)
        right_to_apple = self.euclidean_distance(fruit, right)

        values = [forward_to_apple, left_to_apple, right_to_apple]
        min_indx = values.index(min(values))

        # possible values [0, 1, 2] <- same as output values
        inputs.append(min_indx)

        # angle between head and fruit
        a = np.array([int(snake.body[0].x), int(snake.body[0].y)])
        b = np.array([fruit.x, fruit.y])

        inner = np.inner(a, b)
        norms = np.linalg.norm(a) * np.linalg.norm(b)

        cos = round(inner / norms, 5)

        sin = math.sqrt(1-cos**2)
        inputs.append(sin)

        # get output
        outputs = snake.network.feedforward(inputs)

        # forward left right [0, 1,2]
        direction = {
            0: forward,
            1: left,
            2: right
        }

        max_index = 0
        for i in range(len(outputs)):
            if outputs[i] >= outputs[max_index]:
                max_index = i

        x = direction[max_index].x
        y = direction[max_index].y

        return x, y

    def selectParent(self):
        index = 0
        r = random.random()

        while r > 0:
            r = r - self.population.saved_snakes[index].fitness
            index += 1
        index -= 1

        return self.population.saved_snakes[index]

    def naturalSelection(self):
        new_snakes = []
        for i in range(Population.population):
            parentA = self.selectParent()
            parentB = self.selectParent()
            child = Snake(Population.hidden_node)
            child.network.crossover(
                parentA.network, parentB.network)
            child.network.mutate(GA.mutation_rate)

            new_snakes.append(child)

        self.population.snakes = new_snakes.copy()
        self.generation += 1

    def calculateFitness(self):
        for snake in self.population.saved_snakes:
            fitness = (snake.steps**3) * (3**(snake.score * 3)) - \
                1.5 ** (0.25*snake.steps)
            snake.fitness = round(fitness, 7)
        self.normalize_fitness_value()

    def normalize_fitness_value(self):
        total_sum = 0
        for snake in self.population.saved_snakes:
            total_sum += snake.fitness

        for snake in self.population.saved_snakes:
            snake.fitness = snake.fitness/total_sum
