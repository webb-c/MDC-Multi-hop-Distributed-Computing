from job import JobInfo
from layeredgraph import LayerNode

# info class for making subtask
class SubtaskInfo(JobInfo):
    def __init__(self, job_info: JobInfo, sequence: int, model_index: int, source: LayerNode, destination: LayerNode, computing: float, transfer: float):
        self._sequence = sequence # includes data transfer, dnn computation
        self._model_index = model_index # only includes dnn computation
        self._source = source
        self._destination = destination
        self._computing = computing
        self._transfer = transfer
        
        self._delimeter = "_"

        super().__init__(job_info.get_job_id(), job_info.get_terminal_destination(), job_info.get_job_type(), job_info.get_job_name())

    def get_sequence(self):
        return self._sequence
    
    def get_model_index(self):
        return self._model_index
    
    def get_source(self):
        return self._source
    
    def get_destination(self):
        return self._destination  
    
    def get_computing(self):
        return self._computing

    def get_transfer(self):
        return self._transfer
        
    def get_subtask_id(self):
        return self._delimeter.join([self.get_job_id(), self._source.to_string(), self._destination.to_string(), str(self._sequence)]) # yolo20240312101010_192.168.1.5-0_192.168.1.6-0_1
    
    def is_transmission(self):
        return self._source.is_same_layer(self._destination)
    
    def is_computing(self):
        return self._source.is_same_node(self._destination)