class RoutingTable:
    def __init__(self, address):
        self.address = address
        self.rules = dict()

        if self.address == "192.168.1.6":
            # {id}-{is_response}
            self.add_rule("test-False", "192.168.1.6")
            self.add_rule("test-True", "192.168.1.7")

    def exist_rule(self, id):
        return id in self.rules

    def add_rule(self, id, action):
        self.rules[id] = action

    def del_rule(self, id):
        del self.rules[id]
    
    def find_rule(self, id):
        if self.exist_rule(id):
            return self.rules[id]
        else:
            raise Exception("No flow rules : ", id)