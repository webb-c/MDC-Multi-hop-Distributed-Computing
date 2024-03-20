import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pickle
import time
from threading import Thread
import numpy as np
import cv2
import posix_ipc
import mmap

from utils.utils import get_ip_address
from program import MDC
from job import JobInfo

TARGET_WIDTH = 224
TARGET_HEIGHT = 224
TARGET_DEPTH = 3


class Sender(MDC):
    def __init__(self, sub_config, pub_configs, job_name):
        self._address = get_ip_address("eth0")
        self._frame = None
        self._shape = (TARGET_HEIGHT, TARGET_WIDTH, TARGET_DEPTH)
        self._shared_memory_name = "jetson"
        self._memory = posix_ipc.SharedMemory(self._shared_memory_name, flags=posix_ipc.O_CREAT, mode=0o777, size=int(np.prod(self._shape) * np.dtype(np.uint8).itemsize))
        self._map_file = mmap.mmap(self._memory.fd, self._memory.size)
        # posix_ipc.close_fd(self._memory.fd)

        self._job_name = job_name
        self._job_info = None

        super().__init__(sub_config, pub_configs)

    def init_job_info(self):
        source_ip = self._address
        terminal_destination = self._network_info.get_jobs()[self._job_name]["destination"]
        job_type = self._network_info.get_jobs()[self._job_name]["job_type"]
        job_name = self._job_name

        job_info = JobInfo(source_ip, terminal_destination, job_type, job_name)

        self._job_info = job_info

    def stream_player(self):
        c = np.ndarray(self._shape, dtype=np.uint8, buffer=self._map_file)

        while True:
            self._frame = c.copy()
            print(self._frame.shape)
            if cv2.waitKey(int(1000 / 24)) == ord('q'):
                break

        self._map_file.close()
        self._memory.unlink()

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
        if self._network_info == None:
            try:
                self.init_job_info()
            except:
                pass
        else:
            self._job_info.set_start_time(time.time_ns())

        
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
    sender.run()
