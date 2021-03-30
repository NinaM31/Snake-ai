from pygame.math import Vector2
from Fruit import Fruit
from NN import NeuralNework
import pickle


class Snake:
    def __init__(self, hidden=8):
        self.body = [Vector2(5, 8), Vector2(4, 8), Vector2(3, 8)]
        self.fruit = Fruit()

        self.score = 0
        self.fitness = 0

        self.life_time = 0
        self.steps = 0
        self.hidden = hidden
        self.network = NeuralNework(5, self.hidden, 3)

    def save_model(self, network, name):
        with open(name, "wb") as file:
            pickle.dump(network, file)

    def load_model(self, name):
        with open(name, 'rb') as file:
            self.network = pickle.load(file)

    def reset(self):
        self.body = [Vector2(5, 8), Vector2(4, 8), Vector2(3, 8)]
        self.fruit.reset_seed()

        self.score = 0
        self.fitness = 0
        self.steps = 0

        self.network = NeuralNework(5, self.hidden, 3)

    def get_x(self):
        return self.body[0].x

    def get_y(self):
        return self.body[0].y

    def get_fruit(self):
        return self.fruit.position

    def ate_fruit(self):
        if self.fruit.position == self.body[0]:
            self.score += 1
            self.life_time -= 40
            return True
        return False

    def create_fruit(self):
        self.fruit.generate_fruit()

    def move_ai(self, x, y):
        self.life_time += 1
        self.steps += 1
        for i in range(len(self.body)-1, 0, -1):
            self.body[i].x = self.body[i-1].x
            self.body[i].y = self.body[i-1].y

        self.body[0].x = x
        self.body[0].y = y

    def add_body_ai(self):
        last_indx = len(self.body) - 1
        tail = self.body[-1]
        before_last = self.body[-2]

        if tail.x == before_last.x:
            if tail.y < before_last.y:
                self.body.append(Vector2(tail.x, tail.y-1))
            else:
                self.body.append(Vector2(tail.x, tail.y+1))
        elif tail.y == before_last.y:
            if tail.x < before_last.x:
                self.body.append(Vector2(tail.x - 1, tail.y))
            else:
                self.body.append(Vector2(tail.x + 1, tail.y))

    def ate_body(self):
        for body in self.body[1:]:
            if self.body[0] == body:
                return True
        return False
