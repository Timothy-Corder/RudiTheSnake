import modelReader
modelName = 'sample_model'

neurons, connections = modelReader.parseModel(modelName)

if neurons and connections:
    print("Neurons:")
    for name, neuron in neurons.items():
        print(f"  {name}: {neuron.nType}, threshold={neuron.threshold}")
    
    print("\nConnections:")
    for conn in connections:
        print(f"  {conn.nFrom.name} -> {conn.nTo.name}, weight={conn.weight}")