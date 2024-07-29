import json

class Neuron:
    def __init__(self,nType:str,threshold:float,name:str) -> None:
        if nType not in ['in','out','hidden']:
            raise ValueError('nType must be one of "in", "out" or "hidden"')
        else:
            self.nType = nType
        self.threshold = threshold
        self.name = name
        self.fired = False

class Connection:
    def __init__(self,nFrom:Neuron = None,weight:float = 1.0,nTo:Neuron = None) -> None:
        self.nFrom = nFrom
        self.weight = weight
        self.nTo = nTo
        self.value = 0.0

def parseModel(modelName):
    inputs = \
    {'fillLeft', 'fillRight', 'fillUp', 'fillDown', "length", "appleDistX", "appleDistY"}
    outputs = \
    {
        'left',
        'right',
        'up',
        'down',
    }
    neurons:dict[Neuron] = {}
    
    connections:list[Connection] = []

    try:
        model_file = open(f'{modelName}.model', 'r')
        json_data = json.load(model_file)
        
        # Create Neuron objects
        for neuron_data in json_data.get('neurons', []):
            name = neuron_data['name']
            n_type = neuron_data['type']
            threshold = neuron_data['threshold']
            neurons[name] = Neuron(n_type, threshold, name)
        
        # Create Connection objects
        for conn_data in json_data.get('connections', []):
            from_neuron = neurons[conn_data['from']]
            to_neuron = neurons[conn_data['to']]
            weight = conn_data['weight']
            connections.append(Connection(from_neuron, weight, to_neuron))
        
        print(f"Parsed {len(neurons)} neurons and {len(connections)} connections.")
        
        # You can add additional processing or validation here
        # For example, checking if all input and output neurons are present
        
        return neurons, connections

    except FileNotFoundError:
        print(f"File {modelName} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {modelName}.")
    except KeyError as e:
        print(f"Missing key in JSON data: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        model_file.close()
    return None, None

