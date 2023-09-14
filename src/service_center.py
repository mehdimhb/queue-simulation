from __future__ import annotations
from math_utils import distribution, logistic, update_function, is_boolean_function
from event import EventHeap, ServiceEnd
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simulation import Customer


class Server:
    def __init__(self, server_id):
        self.id = server_id
        self.total_services = 0
        self.total_service_time = 0
        self.total_number_of_served_customer = 0
        self.service_rate = 0
        self.server_utilization = 0
        self.average_served_customer_per_service = 0
        self.average_time_spent_per_customer = 0

    def __repr__(self):
        return str(self.id)


class Service:
    def __init__(self, start: float, end: float, server: Server, customer: Customer) -> None:
        self.start = start
        self.end = end
        self.server = server
        self.customer = customer

    def __repr__(self):
        return f"{self.start}:{self.end} - "+str(self.customer)


class ServerList:
    def __init__(self, no_of_servers: int) -> None:
        self.idle_servers = [Server(i) for i in range(no_of_servers)]
        self.busy_servers = []

    def combine_servers(self) -> list[Server]:
        combination = self.idle_servers[:]
        combination.extend(self.busy_servers)
        return combination

    def is_there_idle_server(self) -> bool:
        return bool(self.idle_servers)

    def get_server(self) -> Server:
        server = self.idle_servers.pop(0)
        self.busy_servers.append(server)
        return server

    def make_idle(self, server: Server) -> None:
        self.busy_servers.remove(server)
        self.idle_servers.append(server)


class ServiceCenter:
    def __init__(
        self,
        event_heap: EventHeap,
        no_of_servers,
        service_distribution,
        priority_service_distribution,
        service_batch_probability,
        service_batch_distribution,
        service_dependency,
        service_dependency_start,
        service_dependency_stop,
        service_dependency_half,
        precision,
        time_update_unit
    ):
        self.events = event_heap
        self.no_of_servers = no_of_servers
        self.service_distribution = service_distribution
        self.priority_service_distribution = priority_service_distribution
        self.service_batch_probability = service_batch_probability
        self.service_batch_distribution = service_batch_distribution
        self.service_dependency = service_dependency
        self.service_dependency_start = service_dependency_start
        self.service_dependency_stop = service_dependency_stop
        self.service_dependency_half = service_dependency_half
        self.precision = precision
        self.time_update_unit = time_update_unit

        self.no_of_customers = 0
        self.all_time_no_customers = 0
        self.average_service_rate = 0
        self.average_server_utilization = 0
        self.average_served_customer_per_service = 0
        self.average_time_spent_per_customer = 0

        self.servers = ServerList(no_of_servers)

    def __len__(self) -> int:
        return self.no_of_customers

    def is_full(self) -> bool:
        return self.servers.is_there_idle_server()

    def remaining_capacity(self) -> int:
        return len(self.servers.idle_servers)

    def no_of_busy_servers(self) -> int:
        return len(self.servers.busy_servers)

    def is_service_batch(self) -> bool:
        return is_boolean_function(self.service_batch_probability)

    def is_service_dependent(self) -> bool:
        return is_boolean_function(self.service_dependency)

    def service_dependency_coefficient(self, length_of_queue: int) -> float:
        return logistic(
            length_of_queue, self.service_dependency_start, self.service_dependency_stop, self.service_dependency_half
        )

    def no_of_customers_in_next_service(self) -> int:
        return round(distribution(self.service_batch_distribution, condition=1), self.precision) \
            if self.is_service_batch() else 1

    def initiate_service(self, customer: list[Customer], start_time: float, length_of_queue: int) -> None:
        service_duration = distribution(
            self.priority_service_distribution if customer[0].priority else self.service_distribution
        )
        service_duration *= self.service_dependency_coefficient(length_of_queue) if self.is_service_dependent() else 1
        self.no_of_customers += len(customer)
        self.all_time_no_customers += len(customer)
        self.events.add(ServiceEnd(Service(
            start_time,
            start_time+service_duration,
            self.servers.get_server(),
            customer
        )))

    def service_end(self, service: Service) -> None:
        self.servers.make_idle(service.server)
        self.no_of_customers -= len(service.customer)

    def update_measure(self, time: float, service: Service = None) -> None:
        if service is not None:
            server = service.server
            service_duration = service.end-service.start
            server.service_rate = update_function(
                server.service_rate,
                server.total_services,
                service_duration,
                1,
                server.total_services+1
            )
            server.total_services += 1
            server.total_service_time += service_duration
            server.average_time_spent_per_customer = update_function(
                server.average_time_spent_per_customer,
                server.total_number_of_served_customer,
                service_duration,
                len(service.customer),
                server.total_number_of_served_customer+len(service.customer)
            )
            server.total_number_of_served_customer += len(service.customer)
            server.average_served_customer_per_service = server.total_number_of_served_customer/server.total_services

        server_utilization, service_rate, served_customer, total_services, time_spent, total_customer = 0, 0, 0, 0, 0, 0
        for server in self.servers.combine_servers():
            server.server_utilization = (server.total_service_time)/time
            server_utilization += server.server_utilization
            service_rate += server.total_services*server.service_rate
            served_customer += server.total_services*server.average_served_customer_per_service
            total_services += server.total_services
            time_spent += server.total_number_of_served_customer*server.average_time_spent_per_customer
            total_customer += server.total_number_of_served_customer
        self.average_server_utilization = server_utilization/self.no_of_servers
        if total_services:
            self.average_service_rate = service_rate/total_services
            self.average_served_customer_per_service = served_customer/total_services
        if total_customer:
            self.average_time_spent_per_customer = time_spent/total_customer
