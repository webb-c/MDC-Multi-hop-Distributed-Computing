import torch

from job import SubtaskInfo, DNNOutput

# DNNSubtask has subtask info, dnn model's pointer.
class DNNSubtask:
    def __init__(self, subtask_info: SubtaskInfo, dnn_model: torch.nn.Module, computing: float, transfer: float):
        self._subtask_info = subtask_info
        self._dnn_model = dnn_model

        # computing and transfer capacity
        self._computing = computing
        self._transfer = transfer

    def get_backlog(self):
        if self._subtask_info.is_transmission():
            return self.get_computing()
        # computing dnn
        elif self._subtask_info.is_computing():
            return self.get_transfer()
        
    def get_computing(self):
        return self._computing
    
    def get_transfer(self):
        return self._transfer
    
    # should distinct transimission vs. computing
    def run(self, data: torch.Tensor):
        # transimission
        if self._subtask_info.is_transmission():
            # just copy the data and make DNNOutput object
            dnn_output = DNNOutput(data.to("cpu"), self._subtask_info)
        # computing dnn
        elif self._subtask_info.is_computing():
            with torch.no_grad():
                output: torch.Tensor = self._dnn_model(data)
            dnn_output = DNNOutput(output.to("cpu"), self._subtask_info)
        
        return dnn_output