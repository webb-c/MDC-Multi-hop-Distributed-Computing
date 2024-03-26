from typing import Tuple, Dict
from job import DNNOutput, SubtaskInfo

import threading
try:
    from time import time_ns
except ImportError:
    from datetime import datetime
    # For compatibility with Python 3.6
    def time_ns():
        now = datetime.now()
        return int(now.timestamp() * 1e9)

class AheadOutputQueue:
    def __init__(self):
        self._dnn_outputs: Dict[SubtaskInfo, Tuple[DNNOutput, int]] = dict()
        self._mutex = threading.Lock()

    def garbage_dnn_output_collector(self, collect_garbage_job_time: int):
        cur_time = time_ns()
        self._mutex.acquire()
        keys_to_delete = [subtask_info for subtask_info, (dnn_output, start_time_nano) in self._dnn_outputs.items() if cur_time - start_time_nano >= collect_garbage_job_time * 1_000_000_000]

        for k in keys_to_delete:
            del self._dnn_outputs[k]

        print(f"Deleted {len(keys_to_delete)} outputs. {len(self._dnn_outputs)} remains.")

        self._mutex.release()

    def exist_dnn_output(self, subtask_info: SubtaskInfo):
        self._mutex.acquire()
        result = subtask_info in self._dnn_outputs
        self._mutex.release()
        return result

    def add_dnn_output(self, subtask_info: SubtaskInfo, dnn_output: DNNOutput):
        print(f"ahead dnn output {subtask_info} added.")
        # ex) "192.168.1.5", Job
        if self.exist_dnn_output(subtask_info):
            return False
        
        else:
            cur_time = time_ns()
            self._dnn_outputs[subtask_info] = (dnn_output, cur_time)
            return True

    def del_dnn_output(self, subtask_info: SubtaskInfo):
        self._mutex.acquire()
        del self._dnn_outputs[subtask_info]
        self._mutex.release()
    
    def find_dnn_output(self, subtask_info: SubtaskInfo):
        if self.exist_dnn_output(subtask_info):
            self._mutex.acquire()
            subtask, _ = self._dnn_outputs[subtask_info]
            self._mutex.release()
            return subtask
        else:
            raise Exception("No flow dnn_outputs : ", subtask_info)
        
    def pop_dnn_output(self, subtask_info: SubtaskInfo):
        print(f"ahead dnn output {subtask_info} poped.")
        dnn_output = self.find_dnn_output(subtask_info)
        self.del_dnn_output(subtask_info)

        return dnn_output
       
    def __str__(self):
        return str(self._dnn_outputs)