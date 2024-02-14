class Job:
    def __init__(self, input):
        self.input = input
        self.output = None
    
    def run(self):
        self.output = self.input

    def get_output(self):
        return self.output