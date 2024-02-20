import time

class Job:
    def __init__(self, input, source, destination, id, info):
        self.input = input
        self.output = None
        self.source = source
        self.rtt_destination = source
        self.destination = destination
        self.start_time = time.time_ns()
        self.response = False
        self.id = id
        self.delimeter = "-"
        self.info = info
    
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
        
    def is_rtt_destination(self, other_address):
        if self.rtt_destination == other_address:
            return True
        else:
            return False
        
    def get_start_time(self):
        return self.start_time
    
    def calc_latency(self):
        time.sleep(0.00000001) # cpu time
        cur_time = time.time_ns()
        return (cur_time - self.start_time) / 1_000_000 # ms
    
    def remove_input(self):
        self.input = None
    
    def is_response(self):
        return self.response
    
    def set_response(self):
        self.response = True

    def get_id(self):
        return self.delimeter.join([self.id, str(self.response)])
    
    def set_source(self, address):
        self.source = address

    def set_destination(self, address):
        self.destination = address
