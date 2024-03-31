from typing import Dict, List

from utils import split_model, load_model
from communication import NetworkInfo

import torch
from calflops import calculate_flops
import sys

class DNNModels:
    def __init__(self, network_info: NetworkInfo, device):
        self._network_info = network_info
        self._device = device

        self._jobs: List[str] = []
        self._subtasks: Dict[str, List[torch.nn.Module]] = dict()
        self._computing_ratios: Dict[str, List[float]] = dict()
        self._transfer_ratios : Dict[str, List[float]] = dict()

        self.init_model()
    
    def init_model(self):
        jobs = self._network_info.get_jobs()
        for job_name in jobs:
            job = jobs[job_name]

            self.add_model(job_name, job)
            self.add_computing_and_transfer(job_name, job)

    def add_model(self, job_name: str, job: Dict):
        # load whole dnn model
        model_name = job["model_name"]

        if "yolo" not in model_name:
            model, flatten_index = load_model(model_name)

            for split_point in job["split_points"]:
                subtask : torch.nn.Module = split_model(model, split_point, flatten_index).to(self._device)
                self.append_subtask(job_name, subtask)

        else:
            models = load_model(model_name)

            for model in models:
                subtask : torch.nn.Module = model.to(self._device)
                self.append_subtask(job_name, subtask)
        
    def add_computing_and_transfer(self, job_name: str, job: Dict):
        if "yolo" in job["model_name"]:
            self._computing_ratios[job_name] = [0, 100, 100, 100, 100] # TODO change to real value
            self._transfer_ratios[job_name] = [1, 10, 10, 10, 1]

            with torch.no_grad():

                x = torch.zeros(job["warmup_input"]).to(self._device)

                for index, subtask in enumerate(self._subtasks[job_name]):
                    x : torch.Tensor = subtask(x)

            print(f"Succesfully load {job_name}")
            return

        computings = torch.zeros(len(self._subtasks[job_name]))
        transfers = torch.zeros(len(self._subtasks[job_name]))

        with torch.no_grad():

            x = torch.zeros(job["warmup_input"]).to(self._device)
            for index, subtask in enumerate(self._subtasks[job_name]):
                input_shape = tuple(x.shape)

                if index == 0:
                    flops = 0
                else:
                    flops, _, _ = calculate_flops(model=subtask, input_shape=input_shape, output_as_string=False, output_precision=4, print_results=False)

                x : torch.Tensor = subtask(x)

                computings[index] = flops
                transfers[index] = sys.getsizeof(x.storage())

        computings = computings / transfers[0] # normalize with input size
        transfers = transfers / transfers[0]

        self._computing_ratios[job_name] = computings.tolist()
        self._transfer_ratios[job_name] = transfers.tolist()

        print(f"Succesfully load {job_name}")

    def append_subtask(self, job_name: str, subtask: torch.nn.Module):
        if job_name not in self._subtasks:
            self._subtasks[job_name] = []
        
        self._subtasks[job_name].append(subtask)

    def append_computing(self, job_name: str, computing: float):
        if job_name not in self._computing_ratios:
            self._computing_ratios[job_name] = []

        self._computing_ratios[job_name].append(computing)

    def append_transfer(self, job_name: str, transfer: float):
        if job_name not in self._transfer_ratios:
            self._transfer_ratios[job_name] = []

        self._transfer_ratios[job_name].append(transfer)
        
    def warmup_model(self, job_name: str, warmup_input: torch.Tensor):
        with torch.no_grad():
            x = warmup_input
            for subtask in self._subtasks[job_name]:
                x : torch.Tensor = subtask(x)
        print(f"Succesfully load {job_name}")

    def get_subtask(self, job_name: str, index: int):
        assert job_name in self._subtasks, f"{job_name} is not exists."
        return self._subtasks[job_name][index]
    
    def get_computing(self, job_name: str, index: int):
        assert job_name in self._computing_ratios, f"{job_name} is not exists."
        return self._computing_ratios[job_name][index]

    def get_transfer(self, job_name: str, index: int):
        assert job_name in self._transfer_ratios, f"{job_name} is not exists."
        return self._transfer_ratios[job_name][index]
