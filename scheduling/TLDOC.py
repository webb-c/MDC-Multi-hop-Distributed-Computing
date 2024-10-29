import heapq
from typing import Dict, List

from layeredgraph import LayerNode, LayerNodePair
import numpy as np
import random, math
from latencymodel.TLDOC import cal_total_latency

class TLDOC:
    def __init__(self, scale=0.1, V=1.0, user_preference=0.1):
        self._scale = scale
        self._V = V
        self._user_preference = user_preference
        self._epoch = 10

    def get_path(self, source_node: LayerNode, destination_node: LayerNode, layered_graph, layered_graph_backlog, layer_nodes, computing_ratios, transfer_ratios, arrival_rate, network_info, input_size):
        #! index 확인 
        max_layer = len(destination_node)
        off_tensor = self._lp_offloading(max_layer, network_info)
        partition_point_1, partition_point_2 = off_tensor[0], off_tensor[0]+off_tensor[1]
        path = self._make_path(source_node, destination_node, layered_graph, partition_point_1, partition_point_2)
        return path
    
    
    def _lp_offloading(self, max_layer, network_info):
        off_tensor = self._create_init_tensor(max_layer)
        count = 0
        for i in range(self._epoch):
            temp_off_tensor = self._create_new_off_tensor(off_tensor, network_info)
            delta = self._objective(temp_off_tensor) - self._objective(off_tensor)
            if delta < 0:
                off_tensor = temp_off_tensor
            else:
                count += 1
            
            if count >= 2:
                break
        
        return off_tensor


    def _create_new_off_tensor(self, off_tensor, network_info):
        # edge-for-cloud -> end-edge-cloud
        #! TODO: 아래와 같이 total_resource 써서 계산해도 제대로 된 값 나오는지 확인
        edge_resource = network_info[0]['edge']
        cloud_resource = network_info[0]['cloud']
        total_resource = edge_resource + cloud_resource
        
        A_end = off_tensor[0]
        delta = int(A_end * self._scale)
        A_end -= delta
        A_edge = off_tensor[1] + int(delta * (edge_resource / total_resource))
        A_cloud = off_tensor[2] + int(delta * (cloud_resource / total_resource))
        
        new_off_tensor = [A_end, A_edge, A_cloud]
        return new_off_tensor
    
    
    def _objective(self):
        pass
    
    def _create_init_tensor(self, max_layer):
        A_end, A_edge, A_cloud = max_layer, 0, 0 
        off_tensor = [A_end, A_edge, A_cloud]
        return off_tensor
    
    
    def _make_requirement(self, computing_ratios, transfer_ratios, partition_point, input_size, arrival_rate):
        """!TODO: requirements 계산방식 확인 (transfer 다 곱셈이 아니라 그냥 그 위치 하나만 곱셈맞는지, arrival rate 어떻게 할건지 확인 필요
        """
        computing_requirements = {
            'end': 0,
            'edge': arrival_rate * sum(computing_ratios[:partition_point]),
            'cloud': arrival_rate * sum(computing_ratios[partition_point:])
        }
        #! check
        transfer_requirements = {
            'end': input_size * arrival_rate,
            'edge': input_size * arrival_rate * transfer_ratios[partition_point], 
            'cloud': 0
        }
        
        return (computing_requirements, transfer_requirements)
    
    
    def _make_path(self, source_node, destination_node, layered_graph, partition_point_1, partition_point_2):
        
        path = []
        path.append(source_node)
        neighbors = layered_graph[source_node][:]
        sorted_neighbors = sorted(neighbors, key=lambda neighbor: neighbor.get_layer())
        
        # end computing
        count = 0
        for node in sorted_neighbors:
            if count >= partition_point_1:
                break 
            
            if source_node.is_same_node(node):
                path.append(node)
                count += 1
        
        end_last_node = node
        neighbors = layered_graph[end_last_node][:]
        sorted_neighbors = sorted(neighbors, key=lambda neighbor: neighbor.get_layer())
        
        # end -> edge
        for node in sorted_neighbors:
            if not end_last_node.is_same_node(node):
                path.append(node)
                break
        
        edge_top_node = node
        neighbors = layered_graph[edge_top_node][:]
        sorted_neighbors = sorted(neighbors, key=lambda neighbor: neighbor.get_layer())
        
        # edge computing
        for node in sorted_neighbors:
            if count >= partition_point_2:
                break 
            
            if edge_top_node.is_same_node(node):
                path.append(node)
                count += 1
        
        edge_last_node = node 
        neighbors = layered_graph[edge_last_node][:]
        sorted_neighbors = sorted(neighbors, key=lambda neighbor: neighbor.get_layer())
        
        # edge -> cloud
        for node in sorted_neighbors:
            if destination_node.is_same_node(node):
                path.append(node)
                break 
        
        cloud_node = node
        cloud_layer = cloud_node.get_layer()
        neighbors = layered_graph[cloud_node][:]
        sorted_neighbors = sorted(neighbors, key=lambda neighbor: neighbor.get_layer())
        
        # cloud computing 
        for node in neighbors:
            if destination_node.is_same_node(node) and cloud_layer < node.get_layer():
                path.append(node)
        
        return path