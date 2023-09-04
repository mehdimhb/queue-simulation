class Customer:
    def __init__(self, arrival_time, priority):
        self.arrival_time = arrival_time
        self.priority = priority

    def __str__(self):
        return str(self.arrival_time)
