from modelReader import Neuron, Connection, parseModel

class NeuralNetwork():
    def __init__(self, neurons:list[Neuron], connections:list[Connection]) -> None:
        self.neurons = neurons
        self.connections = connections

    def activate(self, inputs:dict[Neuron]):
        for name, value in inputs.items():
            if name in self.neurons and self.neurons[name].nType == 'in':
                self.neurons[name].value = value

network = NeuralNetwork()


def aiTick(segs, apl, position, gridSize, length):
    ... 