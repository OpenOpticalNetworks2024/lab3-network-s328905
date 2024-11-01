import json
from typing import Tuple
from math import dist
from scipy.constants import c
import matplotlib.pyplot as plt

class Signal_information(object):
    signal_power: float
    noise_power: float
    latency: float
    path: list[str]

    def __init__(self, signal_power, path):
        self._signal_power = signal_power
        self._noise_power = 0
        self._latency = 0
        self._path = path

    @property
    def signal_power(self): #getter
        return self._signal_power

    def update_signal_power(self, power_increment):
        self._signal_power -= power_increment

    @property
    def noise_power(self):
        return self._noise_power

    @noise_power.setter
    def noise_power(self, noise_value):
        self._noise_power = noise_value

    def update_noise_power(self, noise_increment):
        self._noise_power += noise_increment

    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, latency_value):
        self._latency = latency_value

    def update_latency(self, latency_change):
        self._latency += latency_change

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        self._path = new_path

    def update_path(self):
        self._path.pop(0) #visited node gets removed


class Node(object):
    label: str
    position: Tuple[float, float]
    connected_nodes: list[str]

    def __init__(self, input_dict):
        self._label = input_dict['label']
        self._position = input_dict['position']
        self._connected_nodes = input_dict['connected_nodes']
        self._successive = {}

    @property
    def label(self):
        return self._label

    @property
    def position(self):
        return self._position

    @property
    def connected_nodes(self):
        return self._connected_nodes

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, dict_line):
        self._successive = dict_line

    def propagate(self, signal):
        if len(signal.path) > 1:
            next_line_label = signal.path[0] + signal.path[1]
            signal.update_path()
            next_line = self.successive[next_line_label]
            next_line.propagate(signal)


class Line(object):
    label: str
    length: float

    def __init__(self, label, length):
        self._label = label
        self._length = length
        self._successive = {}

    @property
    def label(self):
        return self._label

    @property
    def length(self):
        return self._length

    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, dict_node):
        self._successive = dict_node

    def latency_generation(self):
        return self._length/(2/3*c)

    def noise_generation(self, signal_power):
        return 1e-9*signal_power*self._length

    def propagate(self, signal):
        signal.update_noise_power(self.noise_generation(signal.signal_power))
        signal.update_latency(self.latency_generation())
        next_node_label = signal.path[0]
        next_node = self.successive[next_node_label]
        next_node.propagate(signal)


class Network(object):
    def __init__(self, input_file):
        with open(input_file, 'r') as file:
            data = json.load(file)
        self._nodes = {}
        self._lines = {}
        for key in data:
            self._nodes[key] = Node({'label' : key, 'position' : data[key]['position'], 'connected_nodes' : data[key]['connected_nodes']})
        for key in self._nodes:
            conn_nodes = self._nodes[key].connected_nodes
            for i in conn_nodes:
                self._lines[key+i] = Line(key+i, dist(self._nodes[key].position, self._nodes[i].position))

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines

    def draw(self):
        plt.figure()
        for line in self._lines.values():
            node1 = self._nodes[line.label[0]]
            node2 = self._nodes[line.label[1]]
            x_pos = [node1.position[0]/1e3, node2.position[0]/1e3]
            y_pos = [node1.position[1]/1e3, node2.position[1]/1e3]
            plt.plot(x_pos, y_pos, 'k-', zorder=1)
        for node in self._nodes.values():
            x_pos = node.position[0]/1e3
            y_pos = node.position[1]/1e3
            plt.scatter(x_pos, y_pos, s=300, zorder=2)
            plt.text(x_pos, y_pos, node.label, ha='center', va='center')
        plt.xlabel('x [km]')
        plt.ylabel('y [km]')
        plt.tight_layout()
        plt.show()

    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once
    def find_paths(self, label1, label2):
        paths = []
        node1 = self._nodes[label1]
        stack = [(node1, [label1])]
        while stack:
            last_visited_node, path = stack.pop()
            if last_visited_node.label == label2:
                paths.append(path)
            for connected_node in last_visited_node.connected_nodes:
                if connected_node not in path:
                    stack.append((self._nodes[connected_node], path + [connected_node]))
        return paths

    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        for node in self._nodes.values():
            for connected_node in node.connected_nodes:
                node.successive[node.label+connected_node] = self._lines[node.label+connected_node]
        for line in self._lines.values():
            line.successive[line.label[1]] = self._nodes[line.label[1]]

    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, signal_information):
        self._nodes[signal_information.path[0]].propagate(signal_information)