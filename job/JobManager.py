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
        self._models : Dict[str, List] = dict()

        self._network_info = network_info

        self._virtual_queue = VirtualQueue(address)

        self.init_models()
        self.init_garbage_job_collector()

    def init_models(self):
        jobs = self._network_info.get_jobs()
        for job_name in jobs:
            job = jobs[job_name]
            if job["job_type"] == "dnn":
                # load whole dnn model
                model_name = job["model_name"]
                model, flatten_index = load_model(model_name)

                # init model list and split model
                self._models[job_name] = []
                for split_point in job["split_points"]:
                    subtask : torch.nn.Module = split_model(model, split_point, flatten_index)
                    self._models[job_name].append(subtask)

                # load models first time
                if job["warmup"]:
                    with torch.no_grad():
                        x = torch.zeros(job["warmup_input"])
                        for subtask in self._models[job_name]:
                            x : torch.Tensor = subtask(x)
                print(f"Succesfully load {job_name}")
                
            elif job["job_type"] == "packet":
                pass

    def is_subtask_exists(self, output: DNNOutput):
        previous_subtask_info = output.get_subtask_info()
        if self._virtual_queue.exist_subtask_info(previous_subtask_info.get_subtask_id()):
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
            data = output.get_output()

            # run job
            dnn_output = subtask.run(data)
            
            print(dnn_output.get_subtask_info())
            dnn_output.get_subtask_info().set_next_subtask_id()
            print(dnn_output.get_subtask_info())

            print("run", dnn_output.get_output().shape)

            return dnn_output

    # add subtask_info based SubtaskInfo
    def add_subtask(self, subtask_info: SubtaskInfo):
        if subtask_info.is_transmission():
            subtask = DNNSubtask(subtask_info, None)

        elif subtask_info.is_computing():
            subtask_model = self._models[subtask_info.get_job_name()][subtask_info.get_model_index()]
            subtask = DNNSubtask(subtask_info, subtask_model)

        success_add_subtask_info = self._virtual_queue.add_subtask_info(subtask_info, subtask)
        print(f"Successfully added job {subtask_info.get_subtask_id()}")
        
        if not success_add_subtask_info:
            raise Exception(f"Subtask already exists. : {subtask_info.get_subtask_id()}")
