from job import SubtaskInfo

class Subtask:
    def __init__(self, subtask_info: SubtaskInfo):
        self._subtask_info = subtask_info

    # should distinct transimission vs. computing
    def run(self, data):
        pass