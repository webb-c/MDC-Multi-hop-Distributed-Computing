import time
from job.Job import Job
from job.DNNJob import DNNJob
import torch
from torchvision.models import resnet18, ResNet18_Weights

class JobManager:
    def __init__(self):
        self.model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        self.model.eval()

    def run(self, job):
        if job.type == "packet":
            job.output = job.input
            return job
        
        elif job.type == "dnn_output":
            self.model(job.input)
            return job


