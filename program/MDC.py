import sys, os
 
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from program import Program
from job import *
from communication import *
from job.JobManager import JobManager
from utils.utils import get_ip_address

import paho.mqtt.publish as publish
import MQTTclient
import pickle
import time

class MDC(Program):
    def __init__(self, sub_config, pub_configs):
        self.sub_config = sub_config
        self.pub_configs = pub_configs
        self._address = get_ip_address(["eth0", "wlan0"])
        self._node_info = NodeInfo(self._address)
        self._controller_publisher = MQTTclient.Publisher(config={
            "ip" : "192.168.1.2",
            "port" : 1883
        })

        self.topic_dispatcher = {
            "job/dnn": self.handle_dnn,
            "job/subtask_info": self.handle_subtask_info,
            "mdc/network_info" : self.handle_network_info,
            "mdc/node_info": self.handle_request_backlog,
        }

        self.topic_dispatcher_checker = {
            "job/dnn": [(self.check_network_info_exists, True)],
            "job/subtask_info": [(self.check_job_manager_exists, True)],
            "mdc/network_info": [(self.check_job_manager_exists, False)],
            "mdc/node_info": [(self.check_job_manager_exists, True)],
        }

        self._network_info = None
        self._job_manager = None
        self._neighbors = None

        super().__init__(self.sub_config, self.pub_configs, self.topic_dispatcher, self.topic_dispatcher_checker)

        self.request_network_info()

    # request network information to network controller
    # sending node info.
    def request_network_info(self):
        while self._network_info == None:
            print("Requested network info..")
            node_info_bytes = pickle.dumps(self._node_info)

            # send NetworkInfo byte to source ip (response)
            self._controller_publisher.publish("mdc/network_info", node_info_bytes)

            time.sleep(10)

    def handle_subtask_info(self, topic, data, publisher):
        subtask_info: SubtaskInfo = pickle.loads(data)

        self._job_manager.add_subtask(subtask_info)
    
    def handle_network_info(self, topic, data, publisher):
        self._network_info: NetworkInfo = pickle.loads(data)
        self._job_manager = JobManager(self._address, self._network_info)

        print(f"Succesfully get network info.")


    def handle_request_backlog(self, topic, data, publisher):
        links = self._job_manager.get_backlogs()
        if len(links) == 0:
            return

        node_link_info = NodeLinkInfo(self._address, links)
        node_link_info_bytes = pickle.dumps(node_link_info)

        # send NodeLinkInfo byte to source ip (response)
        self._controller_publisher.publish("mdc/node_info", node_link_info_bytes)

    def check_network_info_exists(self, data = None):
        if self._network_info == None:
            print("The node is not initialized.")
            return False
        
        elif self._network_info != None:
            return True
        
    def check_job_manager_exists(self, data = None):
        if self._job_manager == None:
            print("The job_manager is not initialized.")
            return False
        
        elif self._job_manager != None:
            return True

    def handle_dnn(self, topic, data, publisher):
        previous_dnn_output: DNNOutput = pickle.loads(data)
        
        # terminal node
        if previous_dnn_output.is_terminal_destination(self._address) and not self._job_manager.is_subtask_exists(previous_dnn_output): 
            subtask_info = previous_dnn_output.get_subtask_info()
            subtask_info_bytes = pickle.dumps(subtask_info)

            # send subtask info to controller
            self._controller_publisher.publish("mdc/response", subtask_info_bytes)

        else: 
            # if this is intermidiate node
            dnn_output = self._job_manager.run(previous_dnn_output)
            subtask_info = dnn_output.get_subtask_info()

            destination_ip = subtask_info.get_destination().get_ip()

            dnn_output_bytes = pickle.dumps(dnn_output)
                
            # send job to next node
            publish.single(f"job/{subtask_info.get_job_type()}", dnn_output_bytes, hostname=destination_ip)
       
if __name__ == '__main__':
    sub_config = {
            "ip": "127.0.0.1", 
            "port": 1883,
            "topics": [
                ("job/dnn", 1),
                ("job/subtask_info", 1),
                ("mdc/network_info", 1),
                ("mdc/node_info", 1),
            ],
        }
    
    pub_configs = [
    ]
    
    mdc = MDC(sub_config=sub_config, pub_configs=pub_configs)
    mdc.start()