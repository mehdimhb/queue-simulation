class Service:
    def __init__(self, start, end, customers):
        self.start = start
        self.end = end
        self.customers = customers

    def __repr__(self):
        return f"{self.start}:{self.end} - "+str(self.customers)


class Server:
    def __init__(self, server_id):
        self.id = server_id
        self._service = None
        self.total_time_of_service = 0
        self.total_time_of_service_definitive = 0
        self.total_number_of_served_customer = 0
        self.service_rate = 0
        self.server_utilization = 0

    @property
    def service(self):
        return self._service

    @service.setter
    def _service(self, srvc):
        self._service = srvc

    def __repr__(self):
        return str(self.id)
