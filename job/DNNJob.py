import time
from job.Job import Job
import torch
from torchvision.models import resnet18

class DNNJob(Job):
    def __init__(self, shape, source, destination, id, info):
        input = torch.ones(shape)
        super.__init__(self, input, source, destination, id, info)
        self.model = resnet18(weights="IMAGENET1K_V2")

    def run(self):
        self.model(input)
