import sys, os, json
 
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from program import Program
from job import Job

import argparse
import pickle
import time

"""

고쳐야할 것:
  - ProgramExample - start
  - config
  - topic_dispathcer


def callback_example(topic, data, publisher):
    print(f"topic: {topic}")
    print(f"data: {data}")

--> 이런 식으로 (topic, data, publisher)를 무조건 받아야함.

"""

class Sender(Program):
    def __init__(self, sub_config, pub_configs):
        self.sub_config = sub_config
        self.pub_configs = pub_configs

        self.topic_dispatcher = {
        }

        super().__init__(self.sub_config, self.pub_configs, self.topic_dispatcher)

    def send_dummy_job(self, data, sleep_time, iterate_time, dst):
        for _ in range(iterate_time):
            dummy_job = Job(data, dst)
            dummy_job_bytes = pickle.dumps(dummy_job)
            self.publisher[0].publish("job/packet", dummy_job_bytes)

            time.sleep(sleep_time)

        
if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-p', '--peer', type=str, default="")
    argparser.add_argument('-t', '--topic', type=str, default="job/packet")
    argparser.add_argument('-g', '--sleep_gap', type=float, default="0.1")
    argparser.add_argument('-s', '--size', type=int, default="100")
    argparser.add_argument('-i', '--iterate', type=int, default="100")
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
    
    sender = Sender(sub_config=sub_config, pub_configs=pub_configs)
    sender.send_dummy_job("0"*args.size, args.sleep_gap, args.iterate, "192.168.1.6")