from typing import Dict
from job import DNNSubtask, SubtaskInfo

import threading

class VirtualQueue:
    def __init__(self, address):
        self.address = address
        self.subtask_infos: Dict[SubtaskInfo, DNNSubtask] = dict()
        self.mutex = threading.Lock()

    def exist_subtask_info(self, id):
        self.mutex.acquire()
        result = id in self.subtask_infos
        self.mutex.release()
        return result

    def add_subtask_info(self, subtask_info, subtask: DNNSubtask):
        # ex) "192.168.1.5", Job
        if self.exist_subtask_info(subtask_info):
            return False
        
        else:
            self.subtask_infos[subtask_info] = subtask
            return True

    def del_subtask_info(self, subtask_info):
        self.mutex.acquire()
        del self.subtask_infos[subtask_info]
        self.mutex.release()
    
    def find_subtask_info(self, subtask_info):
        if self.exist_subtask_info(subtask_info):
            self.mutex.acquire()
            result = self.subtask_infos[subtask_info]
            self.mutex.release()
            return result
        else:
            raise Exception("No flow subtask_infos : ", subtask_info)
        
    def pop_subtask_info(self, subtask_info):
        subtask_info = self.find_subtask_info(subtask_info)
        self.del_subtask_info(subtask_info)

        return subtask_info
    
    def get_backlogs(self):
        links = {}
        self.mutex.acquire()
        for subtask_info in self.subtask_infos:
            subtask: DNNSubtask = self.subtask_infos[subtask_info]

            link = subtask_info.get_link()

            if subtask_info in links:
                links[link] += subtask.get_backlog()
            else:
                links[link] = subtask.get_backlog()

        self.mutex.release()

        return links
        
    def __str__(self):
        return str(self.subtask_infos)