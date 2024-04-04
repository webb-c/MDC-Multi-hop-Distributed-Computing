import heapq
from typing import Dict, List

from layeredgraph import LayerNode, LayerNodePair

import random

class Dijkstra:
    def __init__(self):
        pass

    def get_path(self, source_node: LayerNode, destination_node: LayerNode, layered_graph, layered_graph_backlog, layer_nodes):
        distances = {node: float('infinity') for node in layer_nodes}
        previous_nodes = {node: None for node in layer_nodes}
        
        # Set distance for the source node to zero
        distances[source_node] = 0
        
        pq = [(0, source_node)]

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            # Stop if the destination is reached
            if current_node == destination_node:
                break

            # For each neighbor of the current node
            neighbors = layered_graph[current_node][:]
            random.shuffle(neighbors)
            for neighbor in neighbors:
                neighbor_pair = LayerNodePair(current_node, neighbor)
                neighbor_pair_str = neighbor_pair

                if neighbor_pair_str in layered_graph_backlog:
                    distance = layered_graph_backlog[neighbor_pair_str]
                    new_distance = current_distance + distance

                    # If a shorter path is found
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        previous_nodes[neighbor] = current_node
                        heapq.heappush(pq, (new_distance, neighbor))

        # Path reconstruction from source to destination
        path = []
        current = destination_node
        while current is not None and current in previous_nodes:
            path.append(current)
            current = previous_nodes[current]
        path.reverse()  # Reverse the path to start from the source

        # Use the path for scheduling or further processing
        return path