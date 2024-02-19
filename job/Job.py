import time

class Job:
    def __init__(self, input, source, destination):
        self.input = input
        self.output = None
        self.source = source
        self.destination = destination
        self.start_time = time.time()
        self.response = False
    
    def run(self):
        self.output = self.input

    def get_output(self):
        return self.output
    
    def is_destination(self, other_address):
        if self.destination == other_address:
            return True
        else:
            return False
        
    def is_source(self, other_address):
        if self.source == other_address:
            return True
        else:
            return False
        
    def get_start_time(self):
        return self.start_time
    
    def calc_latency(self):
        return time.time() - self.start_time
    
    def remove_input(self):
        self.input = None
    
    def is_response(self):
        return self.response
    
    def set_response(self):
        self.response = True