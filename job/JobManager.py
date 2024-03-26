from typing import Dict, List
import torch

from job import *
from utils import *
from communication import *
from virtual_queue import VirtualQueue

import threading
import time

class JobManager:
    def __init__(self, address, network_info: NetworkInfo):
        # TODO
        if address != "192.168.1.5":
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self._device = "cpu"

        self._models : Dict[str, List] = dict()

        self._network_info = network_info

        self._virtual_queue = VirtualQueue(address)

        self._dnn_models = DNNModels(self._network_info, self._device)

        print(self._device)
        
        self.init_garbage_job_collector()

    def is_subtask_exists(self, output: DNNOutput):
        previous_subtask_info = output.get_subtask_info()
        if self._virtual_queue.exist_subtask_info(previous_subtask_info):
            return True
        else:
            return False
        
    def init_garbage_job_collector(self):
        callback_thread = threading.Thread(target=self.garbage_job_collector, args=())
        callback_thread.start()

    def garbage_job_collector(self):
        collect_garbage_job_time = self._network_info.get_collect_garbage_job_time()
        while True:
            time.sleep(collect_garbage_job_time)

            self._virtual_queue.garbage_job_collector(collect_garbage_job_time)

    def get_backlogs(self):
        return self._virtual_queue.get_backlogs()

    def run(self, output: DNNOutput) -> DNNOutput:
        previous_subtask_info = output.get_subtask_info()
        if previous_subtask_info.get_job_type() == "dnn":
            # get next destination
            subtask: DNNSubtask = self._virtual_queue.pop_subtask_info(previous_subtask_info)

            # get output data == get current subtask's input
            data = output.get_output().to(self._device)

            # run job
            dnn_output = subtask.run(data)

            return dnn_output

    # add subtask_info based SubtaskInfo
    def add_subtask(self, subtask_info: SubtaskInfo):
        job_name = subtask_info.get_job_name()
        model_index = subtask_info.get_model_index()
        subtask_model = self._dnn_models.get_subtask(job_name, model_index) if subtask_info.is_computing() else None
        computing = self._dnn_models.get_computing(job_name, model_index) * subtask_info.get_input_size()
        transfer = self._dnn_models.get_transfer(job_name, model_index) * subtask_info.get_input_size()

        subtask = DNNSubtask(
            subtask_info = subtask_info,
            dnn_model = subtask_model,
            computing = computing,
            transfer = transfer
        )

        success_add_subtask_info = self._virtual_queue.add_subtask_info(subtask_info, subtask)
        
        if not success_add_subtask_info:
            raise Exception(f"Subtask already exists. : {subtask_info.get_subtask_id()}")
