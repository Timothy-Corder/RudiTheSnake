import json
import random

def create_sample_model(filename, num_hidden=0):
    inputs = [
        "0,0", "0,1", "0,2", "0,3", "0,4",
        "1,0", "1,1", "1,2", "1,3", "1,4",
        "2,0", "2,1", "2,2", "2,3", "2,4",
        "3,0", "3,1", "3,2", "3,3", "3,4",
        "4,0", "4,1", "4,2", "4,3", "4,4",
    ]
    outputs = ['left', 'right', 'up', 'down']
    hidden = []

    for i in range(num_hidden):
        hidden.append({
            "name": f'hidden{i}',
            "type": "hidden",
            "threshold": random.uniform(0.1, 0.9)
        })

    neurons = []
    connections = []

    # Create input neurons
    for input_name in inputs:
        neurons.append({
            "name": input_name,
            "type": "in",
            "threshold": random.uniform(0.1, 0.9)
        })

    # Create output neurons
    for output_name in outputs:
        neurons.append({
            "name": output_name,
            "type": "out",
            "threshold": random.uniform(0.1, 0.9)
        })

    hNames = []
    
    for hNeuron in hidden:
        neurons.append(hNeuron)
        hNames.append(hNeuron['name'])

    ins = inputs
    ins.extend(hNames)
    outs = outputs
    outs.extend(hNames)

    # Create random connections from inputs to outputs
    for input_name in ins:
        for output_name in outs:
            if random.random() < 0.4 and input_name != output_name:  # 40% chance of connection
                connections.append({
                    "from": input_name,
                    "to": output_name,
                    "weight": random.uniform(-1, 1)
                })

    # Create the model dictionary
    model = {
        "neurons": neurons,
        "connections": connections
    }

    # Save the model to a JSON file
    with open(f"{filename}.model", 'w') as f:
        json.dump(model, f, indent=2)

    print(f"Model saved to {filename}.model")
    print(f"Total neurons: {len(neurons)}")
    print(f"Total connections: {len(connections)}")

# Create the sample model
create_sample_model('sample_model', 2)