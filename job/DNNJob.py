import time
from job.Job import Job
import torch
from torchvision.models import resnet18, ResNet18_Weights

class DNNJob(Job):
    def __init__(self, data, source, destination, terminal_destination, id):
        super().__init__(data, source, destination, terminal_destination, id, "dnn")