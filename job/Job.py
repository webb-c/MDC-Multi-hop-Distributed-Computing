import time

class Job:
    def __init__(self, input, destination):
        self.input = input
        self.output = None
        self.destination = destination
        self.start_time = time.time()
    
    def run(self):
        self.output = self.input

    def get_output(self):
        return self.output
    
    def is_destination(self, other_destination):
        if self.destination == other_destination:
            return True
        else:
            return False
        
    def get_start_time(self):
        return self.start_time
    
    def calc_latency(self):
        return time.time() - self.start_time