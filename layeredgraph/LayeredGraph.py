from typing import Dict

from communication import NetworkInfo
from layeredgraph import LayerNode, LayerNodePair
from job import JobInfo
from scheduling import Dijkstra

import importlib
import time

class LayeredGraph:
    def __init__(self, network_info: NetworkInfo):
        self._network_info = network_info
        self._network = network_info.get_network()
        self._layered_graph = dict()
        self._layered_graph_backlog = dict()
        self._layer_nodes = []
        self._layer_node_pairs = []
        self._scheduling_algorithm = None
        self._previous_update_time = time.time()

        self._max_layer_depth = 0

        self.init_graph()
        self.init_algorithm()

    def set_graph(self, links):
        self._previous_update_time = time.time()
        for link in links:
            link: LayerNodePair
            self.set_link(link, links[link])
        
    def update_graph(self):
        current_time = time.time()
        elapsed_time = current_time - self._previous_update_time

        links_job_num = {}

        for link in self._layer_node_pairs:
            link: LayerNodePair
            source_node_ip = link.get_source().get_ip()
            destination_node_ip = link.get_destination().get_ip()

            destinations: Dict = links_job_num.setdefault(source_node_ip, {})
            destinations.setdefault(destination_node_ip, 0)

            if self._layered_graph_backlog[link] > 0:
                destinations[destination_node_ip] += 1

        for source in self._layer_node_pairs:
            link: LayerNodePair
            source_node_ip = link.get_source().get_ip()
            destination_node_ip = link.get_destination().get_ip()
            
            link_job_num = links_job_num[source_node_ip][destination_node_ip]
            capacity = self._network_info.get_capacity()[source_node_ip][destination_node_ip]

            if link_job_num > 0:
                job_computing_delta = elapsed_time * capacity / link_job_num

                self._layered_graph_backlog[link] = max(0, self._layered_graph_backlog[link] - job_computing_delta)

        self._previous_update_time = time.time()

    def set_link(self, link: LayerNodePair, backlog: float):
        self._layered_graph_backlog[link] = backlog

    def init_graph(self):
        self._max_layer_depth = max([len(job["split_points"]) for job_name, job in self._network_info.get_jobs().items()])

        for layer in range(self._max_layer_depth):
            for source_ip in self._network:
                source = LayerNode(source_ip, layer)
                self._layer_nodes.append(source)

                if source not in self._layered_graph:
                    self._layered_graph[source] = []

                for destination_ip in self._network[source_ip]:
                    destination = LayerNode(destination_ip, layer)

                    self._layered_graph[source].append(destination)

                    link = LayerNodePair(source, destination)

                    self._layer_node_pairs.append(link)
                    self._layered_graph_backlog[link] = 0

        for layer in range(self._max_layer_depth - 1):
            for source_ip in self._network:
                source = LayerNode(source_ip, layer)
                destination = LayerNode(source_ip, layer + 1)

                if source not in self._layered_graph:
                    self._layered_graph[source] = []

                self._layered_graph[source].append(destination)

                link = LayerNodePair(source, destination)

                self._layer_node_pairs.append(link)
                self._layered_graph_backlog[link] = 0

        print(self._layered_graph_backlog)

    def init_algorithm(self):
        module_path = self._network_info.get_scheduling_algorithm().replace(".py", "").replace("/", ".")
        self._scheduling_algorithm: Dijkstra = importlib.import_module(module_path).Dijkstra()

    def schedule(self, source_ip: str, job_info: JobInfo):
        split_num = len(self._network_info.get_jobs()[job_info.get_job_name()]["split_points"])
        source_node = LayerNode(source_ip, 0)
        destination_node = LayerNode(job_info.get_terminal_destination(), split_num - 1)
        path = self._scheduling_algorithm.get_path(source_node, destination_node, self._layered_graph, self._layered_graph_backlog, self._layer_nodes)

        return path
    
    def get_neighbors(self, layer_node_ip: str):
        neighbors = []
        for layer in range(self._max_layer_depth):
            layer_node = LayerNode(layer_node_ip, layer)

            neighbor = self._layered_graph[layer_node]

            neighbors += neighbor

        return neighbors
    
    def get_links(self, layer_node_ip: str):
        links = []
        for layer in range(self._max_layer_depth):
            layer_node = LayerNode(layer_node_ip, layer)

            neighbors = self._layered_graph[layer_node]
            for neighbor in neighbors:
                neighbors += neighbor
                link = LayerNodePair(layer_node, neighbor)

                links.append(link)

        return links
    
    

