from job.Job import Job

class DNNJob(Job):
    def __init__(self, data, source, destination, terminal_destination, id):
        super().__init__(data, source, destination, terminal_destination, id, "dnn")