import time
from job.Job import Job
import torch
from torchvision.models import resnet18, ResNet18_Weights

class DNNJob(Job):
    def __init__(self, data, source, destination, id, info):
        # input = torch.ones(data)
        data = torch.ones((1, 3, len(data), len(data)))
        super().__init__(data, source, destination, id, info)
        self.type = "dnn_output"
