
class Neuron:
    def __init__(self,nType:str,threshold:float,name:str) -> None:
        if nType not in ['in','out','hidden']:
            raise ValueError('nType must be one of "in", "out" or "hidden"')
        else:
            self.nType = nType
        self.threshold = threshold
        self.name = name

class Connection:
    def __init__(self,nFrom:Neuron = None,weight:float = 1.0,nTo:Neuron = None) -> None:
        self.nFrom = nFrom
        self.weight = weight
        self.nTo = nTo

def parseModel(modelName):
    inputs = []
    connections = []
    outputs = []
    with open(f'{modelName}.model','rt') as model:
        buffer = ''
        while True:
            buffer += model.read(1)
            if buffer[-1] == ')':
                break
        inVals = buffer.removeprefix('(').removesuffix(')').split(',')
        for i in range(inVals):
            inVals[i] = float(inVals[i])
        print(inVals)

        inNames = ['x','y','aX','aY','direction','left','right','up','down']
        for i in range:
            inputs.append(Neuron('in',inputs[i],inNames[i]))