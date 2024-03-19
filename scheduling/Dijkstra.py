import heapq

from layeredgraph import LayerNode, LayerNodePair

class Dijkstra:
    def __init__(self):
        pass

    def get_path(self, source_node: LayerNode, destination_node: LayerNode, layered_graph, layered_graph_backlog, layer_nodes):
        distances = {node.to_string(): float('infinity') for node in layer_nodes}
        previous_nodes = {node.to_string(): None for node in layer_nodes}
        
        # Set distance for the source node to zero
        distances[source_node.to_string()] = 0
        
        pq = [(0, source_node)]

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            # Stop if the destination is reached
            if current_node == destination_node:
                break

            # For each neighbor of the current node
            for neighbor_ip in layered_graph[current_node.get_ip()]:
                neighbor = LayerNode(neighbor_ip, current_node.get_layer())
                neighbor_pair = LayerNodePair(current_node, neighbor)
                neighbor_pair_str = neighbor_pair.to_string()

                if neighbor_pair_str in layered_graph_backlog:
                    distance = layered_graph_backlog[neighbor_pair_str]
                    new_distance = current_distance + distance

                    # If a shorter path is found
                    if new_distance < distances[neighbor_pair_str]:
                        distances[neighbor.to_string()] = new_distance
                        previous_nodes[neighbor.to_string()] = current_node
                        heapq.heappush(pq, (new_distance, neighbor))

        # Path reconstruction from source to destination
        path = []
        current = destination_node
        while current is not None and current in previous_nodes:
            path.append(current)
            current = previous_nodes[current.to_string()]
        path.reverse()  # Reverse the path to start from the source

        # Use the path for scheduling or further processing
        return path