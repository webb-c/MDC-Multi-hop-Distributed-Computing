from typing import Dict, List
import torch

from job import *
from utils import *
from communication import *
from virtual_queue import VirtualQueue

class JobManager:
    def __init__(self, address, network_info: NetworkInfo):
        self._models : Dict[str, List] = dict()

        self._network_info = network_info

        self._virtual_queue = VirtualQueue(address)

        self.init_models()

    def init_models(self):
        jobs = self._network_info.get_jobs()
        for job_name in jobs:
            job = jobs[job_name]
            if job["job_type"] == "dnn":
                # load whole dnn model
                model_name = job["model_name"]
                model = load_model(model_name).eval()

                # init model list and split model
                self._models[job_name] = []
                for split_point in job["split_points"]:
                    subtask : torch.nn.Module = split_model(model, split_point)
                    self._models[job_name].append(subtask)

                # load models first time
                if job["warmup"]:
                    x = torch.zeros(job["warmup_input"])
                    for subtask in self._models[job_name]:
                        x : torch.Tensor = subtask(x)

            elif job["job_type"] == "packet":
                pass

    def is_subtask_exists(self, output: DNNOutput):
        previous_subtask_info = output.get_subtask_info()
        if self._virtual_queue.exist_rule(previous_subtask_info.get_subtask_id()):
            return True
        else:
            return False
        
    def get_backlogs(self):
        return self._virtual_queue.get_backlogs()

    def run(self, output: DNNOutput) -> DNNOutput:
        previous_subtask_info = output.get_subtask_info()
        if previous_subtask_info.get_job_type() == "dnn":
            # get next destination
            subtask: DNNSubtask = self._virtual_queue.find_rule(previous_subtask_info.get_subtask_id())

            # get output data == get current subtask's input
            data = output.get_output()

            # run job
            dnn_output = subtask.run(data)

            return dnn_output

    # add rule based SubtaskInfo
    def add_subtask(self, subtask_info: SubtaskInfo):
        print(subtask_info._source.to_string())
        print(subtask_info._destination.to_string())
        if subtask_info.is_transmission():
            print("tra")
            subtask_id = subtask_info.get_subtask_id()
            subtask = DNNSubtask(subtask_info, None)

        elif subtask_info.is_computing():
            print("is_computing")
            subtask_id = subtask_info.get_subtask_id()
            subtask_model = self._models[subtask_info.get_job_name()][subtask_info.get_sequence()]
            subtask = DNNSubtask(subtask_info, subtask_model)

        success_add_rule = self._virtual_queue.add_rule(subtask_id, subtask)
            
        if not success_add_rule:
            raise Exception(f"Subtask already exists. : {subtask_info.get_subtask_id()}")
