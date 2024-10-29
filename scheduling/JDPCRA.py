import heapq
from typing import Dict, List

from layeredgraph import LayerNode, LayerNodePair
import numpy as np
import random, math
from latencymodel.JDPCRA import cal_total_latency

class JDPCRA:
    def __init__(self):
        pass

    def get_path(self, source_node: LayerNode, destination_node: LayerNode, layered_graph, layered_graph_backlog, layer_nodes, computing_ratios, transfer_ratios, arrival_rate, network_info, input_size):
        edge_computing_resource = network_info[0]["edge"]
        computing_order, transfer_order = self._cal_order(computing_ratios, transfer_ratios, arrival_rate)
        partition_point = self._init_BS(computing_ratios, computing_order, transfer_order, arrival_rate, edge_computing_resource)
        partition_point = self._Ad_BS(computing_ratios, computing_order, arrival_rate, edge_computing_resource, partition_point)
        
        
        partition_point = self._joint_adjust(computing_ratios, transfer_ratios, arrival_rate, network_info, partition_point, input_size)
        path = self._make_path(source_node, destination_node, layered_graph, partition_point)
        
        return path
    
    
    def _init_BS(self, computing_ratios, computing_order, transfer_order, arrival_rate, edge_computing_resource):
        summed_ratios = np.add(computing_order, transfer_order)
        partition_point = np.argmin(summed_ratios)
        computing_ratio = sum(computing_ratios[:partition_point])
        computing_requirement = arrival_rate * computing_ratio
        
        while edge_computing_resource < computing_requirement:
            temp_partition_point = partition_point
            if computing_order[partition_point] >= 1:
                partition_point = computing_order.index(computing_order[partition_point]-1)
                computing_ratio = sum(computing_ratios[:temp_partition_point])
            
            computing_requirement = arrival_rate * computing_ratio
        
        return partition_point
    
    
    def _Ad_BS(self, computing_ratios, computing_order, arrival_rate, edge_computing_resource, partition_point):
        if computing_order[partition_point] >= 1:
            temp_partition_point = computing_order.index(computing_order[partition_point]-1)
            computing_ratio = sum(computing_ratios[:temp_partition_point])
            computing_requirement = arrival_rate * computing_ratio
            
            if edge_computing_resource < computing_requirement:
                partition_point = temp_partition_point
        
        return partition_point
    
    
    def _joint_adjust(self, computing_ratios, transfer_ratios, arrival_rate, network_info, partition_point, input_size):
        

        task_requirements = self._make_requirement(computing_ratios, transfer_ratios, partition_point, input_size, arrival_rate)
        min_t, stability_info = cal_total_latency(arrival_rate, task_requirements, network_info)
        
        for s in range(len(computing_ratios)):
            temp_task_requirements = self._make_requirement(computing_ratios, transfer_ratios, s, input_size, arrival_rate)
            temp_t, temp_stability_info = cal_total_latency(arrival_rate, temp_task_requirements, network_info)
            if temp_stability_info[0] <= 1 and temp_stability_info[1] <= 1:
                if temp_t < min_t:
                    partition_point = s
                    min_t = temp_t        
        
        return partition_point


    def _cal_order(self, computing_ratios, transfer_ratios, arrival_rate):
        computing_ratios_per_partition_point = []
        for s in range(len(computing_ratios)):
            computing_ratios_per_partition_point.append(arrival_rate * sum(computing_ratios[: s]))
        
        computing_order = np.argsort(computing_ratios_per_partition_point).tolist()
        transfer_order = np.argsort(transfer_ratios).tolist()
        
        return computing_order, transfer_order

    
    def _make_requirement(self, computing_ratios, transfer_ratios, partition_point, input_size, arrival_rate):
        """!TODO: requirements 계산방식 확인 (transfer 다 곱셈이 아니라 그냥 그 위치 하나만 곱셈맞는지 확인 필요
        """
        computing_requirements = {
            'edge': arrival_rate * sum(computing_ratios[:partition_point]),
            'cloud': arrival_rate * sum(computing_ratios[partition_point:])
        }
        transfer_requirements = {
            'edge': input_size * arrival_rate * transfer_ratios[partition_point], #! check
            'cloud': 0
        }
        
        return (computing_requirements, transfer_requirements)
    
    
    def _make_path(self, source_node, destination_node, layered_graph, partition_point):
        
        path = []
        path.append(source_node)
        neighbors = layered_graph[source_node][:]
        sorted_neighbors = sorted(neighbors, key=lambda neighbor: neighbor.get_layer())

        count = 0
        for node in sorted_neighbors:
            if count >= partition_point:
                break 
            
            if source_node.is_same_node(node):
                path.append(node)
                count += 1
        
        edge_node = node 
        
        neighbors = layered_graph[edge_node][:]
        sorted_neighbors = sorted(neighbors, key=lambda neighbor: neighbor.get_layer())
        
        for node in neighbors:
            if destination_node.is_same_node(node):
                path.append(node)
        
        cloud_node = node
        cloud_layer = cloud_node.get_layer()
        
        neighbors = layered_graph[edge_node][:]
        sorted_neighbors = sorted(neighbors, key=lambda neighbor: neighbor.get_layer())
        
        for node in neighbors:
            if destination_node.is_same_node(node) and cloud_layer < node.get_layer():
                path.append(node)
        
        return path