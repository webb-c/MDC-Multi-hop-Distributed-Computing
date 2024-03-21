import heapq
from typing import Dict, List

from layeredgraph import LayerNode, LayerNodePair

class Dijkstra:
    def __init__(self):
        pass

    def get_path(self, source_node: LayerNode, destination_node: LayerNode, layered_graph, layered_graph_backlog, layer_nodes):
        distances = {node: float('infinity') for node in layer_nodes}
        previous_nodes = {node: None for node in layer_nodes}

        print("source_node", source_node)
        print("destination_node", destination_node)
        print("layered_graph", layered_graph)
        print("layered_graph_backlog", layered_graph_backlog)
        print("layer_nodes", layer_nodes)
        
        # Set distance for the source node to zero
        distances[source_node] = 0
        
        pq = [(0, source_node)]

        while pq:
            current_distance, current_node = heapq.heappop(pq)
            print("current_distance", current_distance)
            print("current_node", current_node)

            # Stop if the destination is reached
            if current_node == destination_node:
                break

            # For each neighbor of the current node
            for neighbor_string in layered_graph[current_node]:
                print("neighbor_string", neighbor_string)
                neighbor = LayerNode(neighbor_string.split("-")[0], neighbor_string.split("-")[1])
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
        print(previous_nodes)
        while current is not None and current in previous_nodes:
            path.append(current)
            current = previous_nodes[current]
        path.reverse()  # Reverse the path to start from the source

        # Use the path for scheduling or further processing
        return path