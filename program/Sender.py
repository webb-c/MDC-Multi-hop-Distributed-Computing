import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pickle
import time
from threading import Thread
import paho.mqtt.publish as publish
import numpy as np
import posix_ipc
import mmap
import torch
try:
    from time import time_ns
except ImportError:
    from datetime import datetime
    # For compatibility with Python 3.6
    def time_ns():
        now = datetime.now()
        return int(now.timestamp() * 1e9)

from utils.utils import get_ip_address
from program import MDC
from job import JobInfo, SubtaskInfo, DNNOutput

TARGET_WIDTH = 224
TARGET_HEIGHT = 224
TARGET_DEPTH = 3


class Sender(MDC):
    def __init__(self, sub_config, pub_configs, job_name):
        self._address = get_ip_address(["eth0", "wlan0"])
        self._frame = None
        self._shape = (TARGET_HEIGHT, TARGET_WIDTH, TARGET_DEPTH)
        self._shared_memory_name = "jetson"
        self._memory = posix_ipc.SharedMemory(self._shared_memory_name, flags=posix_ipc.O_CREAT, mode=0o777, size=int(np.prod(self._shape) * np.dtype(np.uint8).itemsize))
        self._map_file = mmap.mmap(self._memory.fd, self._memory.size)
        # posix_ipc.close_fd(self._memory.fd)

        self._job_name = job_name
        self._job_info = None
        self._frame_list = dict()

        super().__init__(sub_config, pub_configs)

    def init_job_info(self):
        source_ip = self._address
        terminal_destination = self._network_info.get_jobs()[self._job_name]["destination"]
        job_type = self._network_info.get_jobs()[self._job_name]["job_type"]
        job_name = self._job_name
        start_time = time_ns()

        job_info = JobInfo(source_ip, terminal_destination, job_type, job_name, start_time)

        self._job_info = job_info

    def handle_subtask_info(self, topic, data, publisher): # overriding
        subtask_info: SubtaskInfo = pickle.loads(data)

        self._job_manager.add_subtask(subtask_info)

        subtask_layer_node = subtask_info.get_source()

        if subtask_layer_node.get_ip() == self._address and subtask_layer_node.get_layer() == 0:
            job_id = subtask_info.get_job_id()
            input_frame = DNNOutput(torch.tensor(self._frame_list[job_id]).float().view(1, TARGET_DEPTH, TARGET_HEIGHT, TARGET_WIDTH), subtask_info)
            dnn_output = self._job_manager.run(input_frame)

            subtask_info = dnn_output.get_subtask_info()

            destination_ip = subtask_info.get_destination().get_ip()

            dnn_output_bytes = pickle.dumps(dnn_output)
                
            # send job to next node
            publish.single(f"job/{subtask_info.get_job_type()}", dnn_output_bytes, hostname=destination_ip)
       
            
    def stream_player(self):
        c = np.ndarray(self._shape, dtype=np.uint8, buffer=self._map_file)

        while True:
            self._frame = c.copy()
            time.sleep(1 / 30)

        self._map_file.close()
        self._memory.unlink()

    def start(self):
        self.wait_until_can_send()

        input("Press any key to start sending.")

        self.run_camera_streamer()

        while True:
            sleep_time = self.get_sleep_time()
            time.sleep(sleep_time)

            self.send_frame()

    def set_job_info_time(self):
        if self._network_info == None:
            return False
        
        else:
            if self._job_info == None:
                self.init_job_info()
                return True
            else:
                self._job_info.set_start_time(time_ns())
                return True
            
    def wait_until_can_send(self):
        while not (self.check_job_manager_exists() and self.check_network_info_exists()):
            print("Waiting for network info.")
            time.sleep(1.0)
            
    def run_camera_streamer(self):
        streamer_thread = Thread(target=self.stream_player, args=())
        streamer_thread.start()

    def send_frame(self):
        if self.set_job_info_time():
            job_info_bytes = pickle.dumps(self._job_info)
            self._frame_list[self._job_info.get_job_id()] = self._frame

            self._controller_publisher.publish("job/request_scheduling", job_info_bytes)
        
    def get_sleep_time(self) -> float:
        # implement any frame drop logic
        return 0.1

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
    
    pub_configs = []

    job_name = "test job 1"

    sender = Sender(sub_config, pub_configs, job_name)
    sender.start()
