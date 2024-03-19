from job import JobInfo

import time

class Job:
    def __init__(self, job_info: JobInfo, subtasks = []):
        self._job_info = job_info
        self._subtasks = subtasks