#TODO: 단위 맞추기

def cal_total_latency(arrival_rate, task_requirements, network_info):
    computing_requirements, transmission_requirements = task_requirements
    computing_capacities, transmission_rates = network_info
    computing_latency = _cal_computing_latency(computing_requirements['edge'], computing_requirements['cloud'], computing_capacities['edge'], computing_capacities['cloud'])
    transmission_latency = _cal_transmission_latency(transmission_rates['edge'], transmission_rates['cloud'], transmission_requirements['edge'], transmission_requirements['cloud'])
    queuing_latency, stability_info = _cal_queueing_latency(arrival_rate, computing_requirements['edge'], computing_requirements['cloud'], computing_capacities['edge'], computing_capacities['cloud'])
    total_latency = arrival_rate * (computing_latency + transmission_latency + queuing_latency)
    
    return total_latency, stability_info


def _cal_computing_latency(edge_computing, cloud_computing, edge_source, cloud_source):
    edge_latency = edge_computing / edge_source
    cloud_latency = cloud_computing / cloud_source
    
    latency = edge_latency + cloud_latency
    return latency


def _cal_transmission_latency(edge_trans_rate, cloud_trans_rate, edge_data_size, cloud_data_size):
    edge_latency = edge_data_size / edge_trans_rate
    cloud_latency = cloud_data_size / cloud_trans_rate
    
    latency = edge_latency + cloud_latency
    return latency


def _cal_queueing_latency(arrival_rate, edge_computing, cloud_computing, edge_source, cloud_source):
    edge_service_rate = edge_source / edge_computing
    cloud_service_rate = cloud_source / cloud_computing
    edge_stability = arrival_rate / edge_service_rate
    cloud_stability = arrival_rate / cloud_service_rate
    stability_info = (edge_stability, cloud_stability)
    
    edge_latency = (arrival_rate / (2*((edge_service_rate)**2)*(1-edge_stability)))
    cloud_latency = 0
    if edge_service_rate > cloud_service_rate:
        cloud_latency = (arrival_rate / (2*((cloud_service_rate)**2)*(1-cloud_stability)))
    
    latency = edge_latency + cloud_latency
    return latency, stability_info