import torch

from job import SubtaskInfo, DNNOutput

# DNNSubtask has subtask info, dnn model's pointer.
class DNNSubtask:
    def __init__(self, subtask_info: SubtaskInfo, dnn_model: torch.nn.Module):
        self._subtask_info = subtask_info
        self._dnn_model = dnn_model

    def get_backlog(self):
        if self._subtask_info.is_transmission():
            return self._subtask_info.get_transfer()
        # computing dnn
        elif self._subtask_info.is_computing():
            return self._subtask_info.get_computing()
    
    # should distinct transimission vs. computing
    def run(self, data: torch.Tensor):
        # transimission
        if self._subtask_info.is_transmission():
            # just copy the data and make DNNOutput object
            dnn_output = DNNOutput(data, self._subtask_info)
        # computing dnn
        elif self._subtask_info.is_computing():
            output: torch.Tensor = self._dnn_model(data)
            dnn_output = DNNOutput(output, self._subtask_info)
        
        return dnn_output