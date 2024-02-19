import sys, os, json
 
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from queue import Queue
from threading import Thread
from program import Program
from datetime import datetime

import argparse
import pickle

from utils.utils import get_ip_address
from routing_table.RoutingTable import RoutingTable
import paho.mqtt.publish as publish

class MDC(Program):
    def __init__(self, sub_config, pub_configs):
        self.sub_config = sub_config
        self.pub_configs = pub_configs
        self.address = get_ip_address("eth0")
        self.routing_table = RoutingTable(self.address)
        print(self.address)

        self.topic_dispatcher = {
            "job/dnn_output": self.handle_dnn_output_in,
            "job/packet": self.handle_packet_in
        }

        super().__init__(self.sub_config, self.pub_configs, self.topic_dispatcher)

    def start(self):
        pass

    def handle_dnn_output_in(self, topic, data, publisher):
        pass

    def handle_packet_in(self, topic, data, publisher):
        dummy_job = pickle.loads(data)

        if dummy_job.is_rtt_destination(self.address):
            print(dummy_job.calc_latency())
            # TODO change to save results.

        elif dummy_job.is_destination(self.address):
            # response to source
            job_id = dummy_job.get_id()
            if self.routing_table.exist_rule(job_id): # if it is mid dst
                destination = self.routing_table.find_rule(job_id)
                dummy_job.set_source(self.address)
                dummy_job.set_destination(destination)
                dummy_job_bytes = pickle.dumps(dummy_job)
                publish.single('job/packet', dummy_job_bytes, hostname=destination)

            else: # if it is final dst
                dummy_job.remove_input()
                dummy_job.set_response()
                dummy_job.set_destination(dummy_job.source)
                dummy_job.set_source(self.address)
                dummy_job_bytes = pickle.dumps(dummy_job)
                publish.single('job/packet', dummy_job_bytes, hostname=dummy_job.destination)

        else:
            dummy_job_bytes = pickle.dumps(dummy_job)
            self.publisher[0].publish('job/packet', dummy_job_bytes)
        
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-p', '--peer', type=str, default="")
    argparser.add_argument('-t', '--topic', type=str, default="job/packet")
    args = argparser.parse_args()

    sub_config = {
            "ip": "127.0.0.1", 
            "port": 1883,
            "topics": [
                (args.topic, 0),
            ],
        }
    
    pub_configs = [
        {
            "ip": args.peer, 
            "port": 1883,
        }
    ]
    
    ex = MDC(sub_config=sub_config, pub_configs=pub_configs)
    ex.start()