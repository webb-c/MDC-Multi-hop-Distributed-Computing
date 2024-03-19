import torch

from communication import *
from job import *

class DNNOutput:
    def __init__(self, data: torch.Tensor, subtask_info: SubtaskInfo) -> None:
        # output tensor
        self._output = data

        # subtask info
        self._subtask_info = subtask_info
        
        # delimeter
        self._delimeter = "-"

    def get_subtask_info(self):
        return self._subtask_info

    def get_output(self):
        return self._output
    
    def is_destination(self, other_address):
        if self._subtask_info.get_destination() == other_address:
            return True
        else:
            return False
        
    def is_terminal_destination(self, other_address):
        if self._dnn_info.get_terminal_destination() == other_address:
            return True
        else:
            return False