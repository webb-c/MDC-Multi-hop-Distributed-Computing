from typing import Dict
from job import DNNSubtask

class VirtualQueue:
    def __init__(self, address):
        self.address = address
        self.rules: Dict[str, DNNSubtask] = dict()

    def exist_rule(self, id):
        return id in self.rules

    def add_rule(self, id, action: DNNSubtask):
        # ex) "192.168.1.5", Job
        if self.exist_rule(id):
            return False
        
        else:
            self.rules[id] = action
            return True

    def del_rule(self, id):
        del self.rules[id]
    
    def find_rule(self, id):
        if self.exist_rule(id):
            return self.rules[id]
        else:
            raise Exception("No flow rules : ", id)
        
    def pop_rule(self, id):
        rule = self.find_rule(id)
        self.del_rule(id)

        return rule
    
    def get_backlogs(self):
        links = {}
        for rule in self.rules:
            subtask: DNNSubtask = self.rules[rule]

            if rule in links:
                links[rule] += subtask.get_backlog()
            else:
                link[rule] = subtask.get_backlog()

        return links
        
    def __str__(self):
        return str(self.rules)