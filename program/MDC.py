import sys, os, json
 
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from queue import Queue
from threading import Thread
from program import Program
from datetime import datetime

import argparse
import pickle


class MDC(Program):
    def __init__(self, sub_config, pub_configs):
        self.sub_config = sub_config
        self.pub_configs = pub_configs

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

        publisher.publish('hardware/server/car_recog/out/from', f'{now}/{car_num}')
        
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-dst', '--destination', type=str, default="")
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
            "ip": args.destination, 
            "port": 1883,
        }
    ]
    
    ex = MDC(sub_config=sub_config, pub_configs=pub_configs)
    ex.start()