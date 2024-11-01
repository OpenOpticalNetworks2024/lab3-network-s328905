import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import core.elements
import itertools
# Exercise Lab3: Network

ROOT = Path(__file__).parent.parent
INPUT_FOLDER = ROOT / 'resources'
file_input = INPUT_FOLDER / 'nodes.json'


# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file

network = core.elements.Network(file_input)

#Connect the network
network.connect()

#Propagate the signal over every possible path
rows = []
for node1, node2 in itertools.permutations(network.nodes,2):
    paths = network.find_paths(node1,node2)
    for path in paths:
        signal = core.elements.Signal_information(1e-3, path)
        tmp = path.copy()
        network.propagate(signal)
        rows.append([f'{'->'.join(tmp)}', signal.latency, signal.noise_power, 10*np.log10(signal.signal_power/signal.noise_power)])
        #if I try to create a new row as a DataFrame and then use pd.concat with a dataframe, on the first iteration I
        #get a FutureWarning since at the beginning the dataframe is empty
df = pd.DataFrame(rows, columns=['Path', 'Total accumulated latency [s]', 'Total accumulated noise [W]', 'SNR [dB]'])
df.to_csv('weighted_path.csv', index=False)

#Plotting the network
network.draw()