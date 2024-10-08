from modelReader import Neuron, Connection, parseModel, writeModel
import math
import random
import copy
import os
import sys

showcase = False
render = True
for arg in sys.argv:
    if arg == '--no-render':
        render = False
for arg in sys.argv:
    if arg == '--showcase':
        showcase = True

class NeuralNetwork():
    def __init__(self, neurons:dict[str, Neuron], connections:list[Connection]) -> None:
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
    
    def toJson(self):
        neurons = []
        for neuron in self.neurons.values():
            neurons.append({
                'name': neuron.name,
                'type': neuron.nType,
                'threshold': neuron.threshold
            })
        connections = []
        for conn in self.connections:
            connections.append({
                'from': conn.nFrom.name,
                'to': conn.nTo.name,
                'weight': conn.weight
            })
        return neurons, connections

def getFitness(score, steps):
    baseScore = score * 100  # Base score for apples eaten

    # Survival bonus that increases logarithmically
    survivalBonus = math.log(steps + 1) * 200  # +1 to avoid log(0)

    # Efficiency bonus (apples per step)
    efficiencyBonus = (score / steps) * 1000 if steps > 0 else 0

    # Exploration bonus (encourages movement)
    explorationBonus = min(steps, 100)  # Cap at 100 to prevent overemphasis on very long games

    # Combine all factors
    fitness = baseScore + survivalBonus + efficiencyBonus + explorationBonus

    return fitness

def loadNetwork():
    global modelName
    with open('usingModel.txt') as nameFile:
        modelName = nameFile.read().strip()
        neurons, connections = parseModel(f'models/{modelName}')
    if not os.path.exists(f'models/trained'):
        os.mkdir(f'models/trained')
    if not os.path.exists(f'models/trained/{modelName}'):
        os.mkdir(f'models/trained/{modelName}')
    return NeuralNetwork(neurons, connections)


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
            

def aiTick(network, segs, apl, position, gridSize, length):
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

# Training time!

def mutateNetwork(network, mutationRate=0.4, mutationRange=0.5, newConnRate=0.2, newNeurRate=0.1, killRate=0.05):
    mutated: NeuralNetwork = copy.deepcopy(network)
    neurons = list(mutated.neurons.values())
    inputs = [n for n in neurons if n.nType == 'in']
    hidden = [n for n in neurons if n.nType == 'hidden']
    outputs = [n for n in neurons if n.nType == 'out']

    # Remove neurons
    for neuron in hidden[:]:  # Create a copy to iterate over
        if random.random() < killRate:
            hidden.remove(neuron)
            del mutated.neurons[neuron.name]
            mutated.connections = [c for c in mutated.connections if c.nFrom != neuron and c.nTo != neuron]
            

    # Add new neuron
    if random.random() < newNeurRate:
        highestHidden = 0
        for neur in hidden:
            name = neur.name
            currHidden = ''
            for char in name:
                try:
                    int(char)
                    currHidden += char
                except:
                    pass
            if int(currHidden) > highestHidden:
                highestHidden = int(currHidden)
            
        newNeuron = Neuron('hidden', random.uniform(-mutationRange, mutationRange), f'hidden{highestHidden+1}')
        possibleFrom = inputs + hidden
        fromNeuron = random.choice(possibleFrom)
        possibleTo = outputs + [n for n in hidden if n != fromNeuron]
        toNeuron = random.choice(possibleTo)

        mutated.connections.append(Connection(fromNeuron, random.uniform(-mutationRange, mutationRange), newNeuron))
        mutated.connections.append(Connection(newNeuron, random.uniform(-mutationRange, mutationRange), toNeuron))
        mutated.neurons[newNeuron.name] = newNeuron
        hidden.append(newNeuron)

    # Add new connection
    if random.random() < newConnRate:
        possibleFrom = inputs + hidden
        fromNeuron = random.choice(possibleFrom)
        possibleTo = outputs + [n for n in hidden if n != fromNeuron]
        toNeuron = random.choice(possibleTo)
        mutated.connections.append(Connection(fromNeuron, random.uniform(-mutationRange, mutationRange), toNeuron))

    # Mutate existing connections
    for conn in mutated.connections:
        if random.random() < mutationRate:
            conn.weight += random.uniform(-mutationRange, mutationRange)

    # Mutate neuron thresholds
    for neuron in neurons:
        if random.random() < mutationRate:
            neuron.threshold += random.uniform(-mutationRange, mutationRange)
    
    # Remove a connection
    for conn in range(mutated.connections.__len__()).__reversed__():
        if random.random() < killRate:
            del mutated.connections[conn-1]
            break

    return mutated

def trainNetwork(generations = 300, population = 200, survivorDivisor = 2):
    pop = 0
    highestFitness = 0
    
    def trainSort(net:NeuralNetwork):
        nonlocal pop, highestFitness
        from game import SnakeGame

        game = SnakeGame(net, render)
        length, moves = game.start()
        game.cleanup()
        fitness = getFitness(length, moves)
        pop += 1
        print(f'Member {pop} died with fitness {fitness}')
        if fitness > highestFitness:
            highestFitness = fitness
        return fitness
        
    seedNetwork = loadNetwork()
    networks = []
    # Create and sort the first generation
    for _ in range(population):
        networks.append(mutateNetwork(seedNetwork))
    
    for gen in range(generations):
        pop = 0
        print(f"Training Generation {gen}")
        # Sort the networks by their fitness
        networks.sort(key=trainSort, reverse=True)
        
        # Kill the unfit networks
        networks = networks[:(population // survivorDivisor)]
        netCount = len(networks)
        for __ in range(survivorDivisor - 1):
            for network in networks[:netCount]:
                networks.append((mutateNetwork(network)))
        
        neurons, connections = networks[0].toJson()
        writeModel(f'models/trained/{modelName}/gen{gen} ({round(highestFitness)})', neurons, connections)
        print(f'Finished training generation {gen}. Highest fitness was {highestFitness}')

if not showcase:
    trainNetwork(survivorDivisor=10)
else:
    network = loadNetwork()
    from game import SnakeGame
    while True:
        game = SnakeGame(network, show = True)
        game.start()