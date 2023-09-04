class Server:
    def __init__(self, server_id):
        self.id = server_id
        self.time_of_begining_service = 0
        self.time_of_ending_service = 0
        self.customers = []
        self.total_time_of_service = 0
        self.total_time_of_service_definitive = 0
        self.total_number_of_served_customer = 0
        self.service_rate = 0
        self.server_utilization = 0

    def __str__(self):
        c = [str(x) for x in self.customers]
        return str(f"({self.id}, {self.time_of_begining_service}, \
                   {self.time_of_ending_service}, {c})")
