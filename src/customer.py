class Customer:
    def __init__(self, id, arrival_time, priority):
        self.id = id
        self.arrival_time = arrival_time
        self.priority = priority

    def __repr__(self):
        return str(self.id)
