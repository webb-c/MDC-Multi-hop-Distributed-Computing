import sys, os
 
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pickle
import time
from multiprocessing import shared_memory
from threading import Thread

import numpy as np
import cv2

from utils.utils import get_ip_address
from program import MDC
from job import JobInfo


TARGET_WIDTH = 224
TAREGET_HEIGHT= 224
TARGET_DEPTH = 3


class Sender(MDC):
    def __init__(self, sub_config, pub_configs, job_name):
        self._address = get_ip_address("eth0")
        self._frame = None
        self._shape = (TAREGET_HEIGHT, TARGET_WIDTH, TARGET_DEPTH)
        self._shared_memory_name = "jetson"
        self._shared_memory = shared_memory.SharedMemory(name=self._shared_memory_name)

        self._job_name = job_name
        self._job_info = None

        super().__init__(sub_config, pub_configs)

        self.init_job_info()

    def init_job_info(self):
        source_ip = self._address
        terminal_destination = self._network_info.get_jobs()[self._job_name]["destination"]
        job_type = self._network_info.get_jobs()[self._job_name]["job_type"]
        job_name = self._job_name

        job_info = JobInfo(source_ip, terminal_destination, job_type, job_name)

        self._job_info = job_info

    def stream_player(self):
        c = np.ndarray(self._shared_memory_name, dtype=np.uint8, buffer=self._shared_memory.buf)

        while True:
            self._frame = c
            if cv2.waitKey(int(1000 / 24)) == ord('q'):
                break

        self._shared_memory.unlink()
        self._shared_memory.close()

    def run(self):
        streamer_thread = Thread(target=self.stream_player, args=())

        streamer_thread.start()

        while True:
            # with any frame drop logic
            time.sleep(0.03)
            self.set_job_info_time()

            job_info_bytes = pickle.dumps(self._job_info)

            self._controller_publisher.publish("job/dnn", job_info_bytes)

    def set_job_info_time(self):
        self._job_info.set_start_time(time.time_ns())

        
if __name__ == '__main__':
    sub_config = {
    }
    
    pub_configs = []

    job_name = "test job 1"

    sender = Sender(sub_config, pub_configs, job_name)
    sender.run()



