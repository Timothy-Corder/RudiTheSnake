from modelReader import Neuron, Connection, parseModel
import math

class NeuralNetwork():
    def __init__(self, neurons:dict[Neuron], connections:list[Connection]) -> None:
        self.neurons = neurons
        self.connections = connections
        self.sortedNeurons = self._topological_sort()

    def _topological_sort(self):
        # Kahn's algorithm for topological sorting. Made with assistance from ClaudeAI
        in_degree = {n: 0 for n in self.neurons.values()}
        for conn in self.connections:
            in_degree[conn.nTo] += 1

        queue = [n for n in self.neurons.values() if in_degree[n] == 0]
        sorted_neurons = []

        while queue:
            n = queue.pop(0)
            sorted_neurons.append(n)
            for conn in self.connections:
                if conn.nFrom == n:
                    in_degree[conn.nTo] -= 1
                    if in_degree[conn.nTo] == 0:
                        queue.append(conn.nTo)

        if len(sorted_neurons) != len(self.neurons):
            raise ValueError("Graph has a cycle")

        return sorted_neurons

    def activate(self, inputs:dict):
        # Reset all neuron values
        for neuron in self.neurons.values():
            neuron.value = 0.0

        # Set input values
        for name, value in inputs.items():
            if name in self.neurons and self.neurons[name].nType == 'in':
                self.neurons[name].value = value

        # Propagate values through the network
        for neuron in self.sortedNeurons:
            if neuron.nType != 'in':
                incomingConnections = [conn for conn in self.connections if conn.nTo == neuron]
                neuron.value = sum(conn.nFrom.value * conn.weight for conn in incomingConnections)
                neuron.value = self.sigmoid(neuron.value)

        # Get output
        output = {}
        for name, neuron in self.neurons.items():
            if neuron.nType == 'out':
                output[name] = neuron.value > neuron.threshold

        return output

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + math.exp(-x))

def getFitness(score, steps, max_steps):
    length_fitness = score * 100  # Prioritize snake length
    efficiency = max(0, 1 - (steps / max_steps))  # Reward efficiency
    survival_bonus = min(1, steps / max_steps) * 50  # Reward survival time
    return length_fitness + (efficiency * 100) + survival_bonus 

def loadNetwork():
    global network
    with open('usingModel.txt') as nameFile:
        modelName = nameFile.read().strip()
        neurons, connections = parseModel(modelName)
    return NeuralNetwork(neurons, connections)

network = loadNetwork()

def checkSeg(segments, x, y, useHead = False, useEdges = True, useTail = False):
    if x < 0 or y < 0 or x > grid['x'] or y > grid['y'] and useEdges:
        return True
    if not useTail:
        sgmnts = segments[1:]
    else:
        sgmnts = segments
    if not useHead:
        sgmnts = sgmnts[:-1]
    for segment in sgmnts:
        try:
            if segment.x == x and segment.y == y:
                return True
        except AttributeError:
            pass
    return False

def fillCheck(sgmnts, x, y):
    checked = []
    def check(x, y):
        nonlocal checked
        if (x,y) in checked:
            return 0
        checked.append((x, y))
        if checkSeg(sgmnts, x, y, True, True, True):
            return 0
        else:
            safe = check(x+1, y) + check(x+1, y) + check(x, y+1) + check(x, y-1)
            return safe + 1
    return check(x, y)
            

def aiTick(segs, apl, position, gridSize, length):
    global grid
    grid = gridSize
    # 'fillLeft', 'fillRight', 'fillUp', 'fillDown', 'length', 'appleDistX', 'appleDistY'
    inputs = {}

    x, y = position
    inputs['length'] = length
    inputs['fillLeft'] = fillCheck(segs, x-1, y)
    inputs['fillRight'] = fillCheck(segs, x+1, y)
    inputs['fillUp'] = fillCheck(segs, x, y-1)
    inputs['fillDown'] = fillCheck(segs, x, y+1)
    inputs['appleDistX'] = x - apl.x
    inputs['appleDistY'] = y - apl.y

    outputs = network.activate(inputs)

    return outputs