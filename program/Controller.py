import sys, os, time
 
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from program import Program
from communication import *
from layeredgraph import LayeredGraph, LayerNode
from job import JobInfo, SubtaskInfo
from utils import save_latency

import pickle, json
import paho.mqtt.publish as publish
import threading

class Controller(Program):
    def __init__(self, sub_config, pub_configs):
        self.sub_config = sub_config
        self.pub_configs = pub_configs

        self.topic_dispatcher = {
            "mdc/network_info": self.handle_network_info,
            "mdc/node_info": self.handle_node_info,
            "job/request_scheduling": self.handle_request_scheduling,
            "job/response": self.handle_response,
        }

        self.topic_dispatcher_checker = {}

        super().__init__(self.sub_config, self.pub_configs, self.topic_dispatcher)

        self._log_path = None
        self._network_info: NetworkInfo = None
        self._layered_graph = None
        
        self._job_list = {}
        self._job_list_mutex = threading.Lock()

        self.init_network_info()
        self.init_path()
        self.init_layered_graph()
        self.init_garbage_job_collector()

    def init_network_info(self):
        with open("config.json", 'r') as file:
            netork_info = NetworkInfo(json.load(file))
            self._network_info = netork_info

    def init_path(self):
        self._log_path = f"./results/{self._network_info.get_experiment_name()}"
        os.makedirs(self._log_path, exist_ok=True)
        
    def init_layered_graph(self):
        self._layered_graph = LayeredGraph(self._network_info)

    def init_garbage_job_collector(self):
        callback_thread = threading.Thread(target=self.garbage_job_collector, args=())
        callback_thread.start()

    def garbage_job_collector(self):
        collect_garbage_job_time = self._network_info.get_collect_garbage_job_time()
        while True:
            time.sleep(collect_garbage_job_time)

            cur_time = time.time_ns()

            self._job_list_mutex.acquire()
            keys_to_delete = [job_id for job_id, start_time_nano in self._job_list.items() if cur_time - start_time_nano >= collect_garbage_job_time * 1_000_000_000]
            for k in keys_to_delete:
                del self._job_list[k]

            print(f"Deleted {len(keys_to_delete)} jobs. {len(self._job_list)} remains.")

            self._job_list_mutex.release()

    def handle_network_info(self, topic, payload, publisher):
        # get source ip address
        node_info: NodeInfo = pickle.loads(payload)
        ip = node_info.get_ip()

        print(f"ip: {ip} requested network information.")

        # make NetworkInfo & NetworkInfo byte
        network_info_bytes = pickle.dumps(self._network_info)

        # send NetworkInfo byte to source ip (response)
        publish.single("mdc/network_info", network_info_bytes, hostname=ip)

        print(f"Succesfully respond to ip: {ip}.")

    def sync_backlog(self):
        for node_ip in self._network_info.get_network():
            # send RequestBacklog byte to source ip (response)
            request_backlog = RequestBacklog()
            request_backlog_bytes = pickle.dumps(request_backlog)
            try:
                publish.single("mdc/node_info", request_backlog_bytes, hostname=node_ip)
            except:
                pass

    def handle_node_info(self, topic, payload, publisher):
        node_link_info: NodeLinkInfo = pickle.loads(payload)
        links = node_link_info.get_links()

        total_links = self._layered_graph.get_links(node_link_info.get_ip())

        for link in total_links:
            links.setdefault(link, 0)

        self._layered_graph.set_graph(links)

    def handle_request_scheduling(self, topic, payload, publisher):
        self._layered_graph.update_graph()
        job_info: JobInfo = pickle.loads(payload)

        print(f"got {job_info.get_job_id()}")

        # register start time
        self._job_list[job_info.get_job_id()] = time.time_ns()

        path = self._layered_graph.schedule(job_info.get_source_ip(), job_info)

        if path[0].is_same_node(path[1]) and not path[0].is_same_layer(path[1]):
            model_index = 1
        else:
            model_index = 0
        
        for i in range(len(path) - 1):
            source_layer_node: LayerNode = path[i]
            destination_layer_node: LayerNode = path[i + 1]
            future_destination_layer_node: LayerNode = path[i + 2] if i + 1 < len(path) else None

            computing = self._network_info.get_jobs()[job_info.get_job_name()]["computing"][model_index]
            transfer = self._network_info.get_jobs()[job_info.get_job_name()]["transfer"][model_index]

            subtask_info = SubtaskInfo(job_info, i, model_index, source_layer_node, destination_layer_node, future_destination_layer_node, computing, transfer)
            subtask_info_bytes = pickle.dumps(subtask_info)

            if i != 0 and source_layer_node.is_same_node(destination_layer_node) and not source_layer_node.is_same_layer(destination_layer_node):
                model_index += 1

            # send SubtaskInfo byte to source ip
            publish.single("job/subtask_info", subtask_info_bytes, hostname=source_layer_node.get_ip())
            
    def handle_response(self, topic, payload, publisher):
        subtask_info: SubtaskInfo = pickle.dumps(payload)
        start_time = self._job_list[subtask_info.get_job_id()]
        finish_time = time.time_ns()

        latency = finish_time - start_time
        file_path = f"{self._log_path}/{subtask_info.get_job_name()}"
        save_latency(file_path, latency)

    def start(self):
        while True:
            time.sleep(self._network_info.get_sync_time())
            self.sync_backlog()


if __name__ == '__main__':

    sub_config = {
            "ip": "127.0.0.1", 
            "port": 1883,
            "topics": [
                ("mdc/network_info", 1),
                ("mdc/response", 1),
                ("mdc/node_info", 1),
                ("job/request_scheduling", 1),
            ],
        }
    
    pub_configs = []
    
    controller = Controller(sub_config=sub_config, pub_configs=pub_configs)
    controller.start()