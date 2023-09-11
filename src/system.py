from service_center import ServiceCenter
from queue import Queue


class System:
    def __init__(
        self,
        queue_capacity,
        no_of_servers,
        service_distribution,
        service_batch_probability,
        service_batch_distribution,
        service_dependency,
        service_dependency_start,
        service_dependency_stop,
        service_dependency_half,
        server_select_rand_probability,
        priority_service_distribution,
        bulk,
        bulk_start,
        bulk_stop,
        bulk_half,
        renege,
        renege_start,
        renege_stop,
        renege_half,
        discipline,
        t_star,
        k_star
    ):
        # system properties
        self.queue_capacity = queue_capacity
        self.no_of_servers = no_of_servers

        # service properties
        self.service_distribution = service_distribution
        self.service_batch_probability = service_batch_probability
        self.service_batch_distribution = service_batch_distribution
        self.service_dependency = service_dependency
        self.service_dependency_start = service_dependency_start
        self.service_dependency_stop = service_dependency_stop
        self.service_dependency_half = service_dependency_half
        self.server_select_rand_probability = server_select_rand_probability
        self.priority_service_distribution = priority_service_distribution

        # queue behavior and discipline
        self.bulk = bulk
        self.bulk_start = bulk_start
        self.bulk_stop = bulk_stop
        self.bulk_half = bulk_half
        self.renege = renege
        self.renege_start = renege_start
        self.renege_stop = renege_stop
        self.renege_half = renege_half
        self.discipline = discipline

        # statistics
        self.t_star = t_star
        self.k_star = k_star

        self.service_center = ServiceCenter()
        self.queue = Queue()
