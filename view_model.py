import json
import graphviz

def create_neural_network_graph(json_data):
    # Parse the JSON data
    data = json.loads(json_data)
    
    # Create a new directed graph
    dot = graphviz.Digraph(comment='Neural Network')
    dot.attr(rankdir='LR')  # Left to Right layout
    
    # Create nodes (neurons)
    for neuron in data['neurons']:
        node_color = {
            'in': 'lightblue',
            'out': 'lightgreen',
            'hidden': 'lightyellow'
        }.get(neuron['type'], 'white')
        
        dot.node(neuron['name'], 
                 f"{neuron['name']}\\n({neuron['type']})", 
                 style='filled', 
                 fillcolor=node_color)
    
    # Create edges (connections)
    for conn in data['connections']:
        dot.edge(conn['from'], conn['to'], 
                 label=f"{conn['weight']:.2f}")
    
    return dot

# Read the JSON data from file
with open('models/Gen 36-23-27.model', 'r') as file:
    json_data = file.read()

# Create the graph
graph = create_neural_network_graph(json_data)

# Render the graph
graph.render('neural_network', format='png', cleanup=True)
print("Neural network visualization has been saved as 'neural_network.png'")