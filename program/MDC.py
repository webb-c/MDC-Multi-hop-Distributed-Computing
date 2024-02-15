import sys, os, json
 
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from queue import Queue
from threading import Thread
from program import Program
from datetime import datetime

import argparse
import pickle


class MDC(Program):
    def __init__(self, sub_config, pub_configs, address):
        self.sub_config = sub_config
        self.pub_configs = pub_configs
        self.address = address

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

        if dummy_job.is_destination(self.address):
            print(dummy_job.calc_latency())
        else:
            dummy_job_bytes = pickle.dumps(dummy_job)
            self.publisher[0].publish('job/packet', dummy_job_bytes)
        
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-p', '--peer', type=str, default="")
    argparser.add_argument('-a', '--address', type=str, default="")
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
    
    ex = MDC(sub_config=sub_config, pub_configs=pub_configs, address=args.address)
    ex.start()