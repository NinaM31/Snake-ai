import numpy as np
import math
from Algorithm import Algorithm
from Constants import USER_SEED

np.random.seed(USER_SEED)


def sigmoid(m):
    return 1/(1+np.exp(-m))


def ReLU(x):
    return x * (x > 0)


def tanh(x):
    return np.tanh(x)


class NeuralNework:
    def __init__(self, input_nodes, hidden_nodes, output_nodes):
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes
        self.shape = (input_nodes, hidden_nodes, output_nodes)

        self.initialize()

    def initialize(self):
        self.biases = [np.random.randn(i)
                       for i in [self.hidden_nodes, self.output_nodes]]
        self.weights = [np.random.randn(j, i)
                        for i, j in zip([self.input_nodes, self.hidden_nodes], [self.hidden_nodes, self.output_nodes])]

    def feedforward(self, input_matrix):
        input_matrix = np.array(input_matrix)
        for b, w in zip(self.biases, self.weights):
            input_matrix = tanh(np.dot(w, input_matrix)+b)
        return input_matrix

    def crossover(self, networkA, networkB):
        weightsA = networkA.weights.copy()
        weightsB = networkB.weights.copy()

        biasesA = networkA.biases.copy()
        biasesB = networkB.biases.copy()

        for i in range(len(self.weights)):
            length = len(self.weights[i])
            split = np.random.uniform(0, 1, size=length)
            split = np.random.randint(1, length)
            self.weights[i] = weightsA[i].copy()
            self.weights[i][split > 0.5] = weightsB[i][split > 0.5].copy()

        for i in range(len(self.biases)):
            length = len(self.biases[i])
            split = np.random.randint(1, length)
            self.biases[i] = biasesA[i].copy()
            self.biases[i][:split] = biasesB[i][:split].copy()

    def mutation(self, a, val):
        if np.random.rand() < val:
            return np.random.randn()
        return a

    def mutate(self, val):
        muation = np.vectorize(self.mutation)

        for i in range(len(self.weights)):
            self.weights[i] = muation(self.weights[i], val)

        for i in range(len(self.biases)):
            self.biases[i] = muation(self.biases[i], val)

    def print(self):
        print('shape', self.shape)
        print('weights', self.weights)
        print('biases', self.biases)
