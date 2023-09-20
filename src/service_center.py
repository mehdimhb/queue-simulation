from __future__ import annotations
import numpy as np
from . import PRECISION
from src.math_utils import distribution, logistic, update_function, boolean_function
from src.event import ServiceEnd
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from src.simulation import Customer
    from src.event import EventHeap


class Server:
    def __init__(self, server_id: int) -> None:
        self.id = server_id
        self.status: Literal['idle', 'busy'] = "idle"
        self.no_of_served_customers: int = 0
        self.no_of_unserved_customers: int = 0
        self.average_time_spent_per_customer: float = 0
        self.no_of_services: int = 0
        self.no_of_unfinished_services: int = 0
        self.total_service_time: float = 0
        self.system_time: float = 0

    @property
    def service_rate(self) -> float:
        if self.total_service_time == 0:
            return 0
        return round(self.no_of_served_customers/self.total_service_time, PRECISION)

    @property
    def server_utilization(self) -> float:
        if self.system_time == 0:
            return 0
        return round(self.total_service_time/self.system_time, PRECISION)

    @property
    def average_service_batch_size(self) -> float:
        if (self.no_of_services+self.no_of_unfinished_services) == 0:
            return 0
        return round(
            (self.no_of_served_customers+self.no_of_unserved_customers)/(self.no_of_services+self.no_of_unfinished_services),
            PRECISION
        )

    def __repr__(self) -> str:
        return f"{self.id}:{self.status}"


class Service:
    def __init__(self, start: float, end: float, server: Server, customer: list[Customer]) -> None:
        self.start = start
        self.end = end
        self.server = server
        self.customer = customer

    def __repr__(self) -> str:
        return f"server:{self.server} - customer{self.customer} - {self.start}:{self.end}"


class ServerList:
    def __init__(self, no_of_servers: int) -> None:
        self.idle_servers: list[Server] = [Server(i) for i in range(no_of_servers)]
        self.busy_servers: list[Server] = []

    def __repr__(self) -> str:
        return str(self.combine_servers())

    def combine_servers(self) -> list[Server]:
        combination = self.idle_servers[:]
        combination.extend(self.busy_servers)
        return combination

    def is_there_idle_server(self) -> bool:
        return bool(self.idle_servers)

    def get_server(self) -> Server:
        i = np.random.randint(len(self.idle_servers))
        server = self.idle_servers.pop(i)
        self.busy_servers.append(server)
        server.status = "busy"
        return server

    def make_idle(self, server: Server) -> None:
        self.busy_servers.remove(server)
        self.idle_servers.append(server)
        server.status = "idle"


class ServiceCenter:
    def __init__(
        self,
        event_heap: EventHeap,
        no_of_servers: int,
        service_distribution: str,
        priority_service_distribution: str,
        service_batch_probability: float,
        service_batch_distribution: str,
        service_dependency: bool,
        service_dependency_start: int,
        service_dependency_half: int,
        service_dependency_stop: int,
        time_precision: int,
    ) -> None:
        self.events = event_heap
        self.no_of_servers = no_of_servers
        self.service_distribution = service_distribution
        self.priority_service_distribution = priority_service_distribution
        self.service_batch_probability = service_batch_probability
        self.service_batch_distribution = service_batch_distribution
        self.service_dependency = service_dependency
        self.service_dependency_start = service_dependency_start
        self.service_dependency_half = service_dependency_half
        self.service_dependency_stop = service_dependency_stop
        self.time_precision = time_precision

        self.no_of_customers: int = 0
        self.average_no_of_customers: float = 0

        self.last_data: dict[str, int | float] = {'time': 0, 'number': 0}
        self.servers = ServerList(no_of_servers)
        self.unfinished_services: list[Service] = []

    @property
    def average_time_spent_per_customer(self):
        return self.average_among_servers('average_time_spent_per_customer', 'no_of_served_customers')

    @property
    def average_service_rate(self):
        return self.average_among_servers('service_rate', 'total_service_time')

    @property
    def service_rate(self):
        return round(sum([server.service_rate for server in self.servers.combine_servers()]), PRECISION)

    @property
    def average_server_utilization(self):
        return round(np.mean([server.server_utilization for server in self.servers.combine_servers()]), PRECISION)

    @property
    def average_service_batch_size(self):
        return self.average_among_servers('average_service_batch_size', 'no_of_services')

    def __len__(self) -> int:
        return self.no_of_customers

    def is_full(self) -> bool:
        return not self.servers.is_there_idle_server()

    def remaining_capacity(self) -> int:
        return len(self.servers.idle_servers)

    def no_of_busy_servers(self) -> int:
        return len(self.servers.busy_servers)

    def is_service_batch(self) -> bool:
        return boolean_function(self.service_batch_probability)

    def is_service_dependent(self) -> bool:
        return boolean_function(self.service_dependency)

    def service_dependency_coefficient(self, length_of_queue: int) -> float:
        return logistic(
            length_of_queue, self.service_dependency_start, self.service_dependency_half, self.service_dependency_stop
        )

    def no_of_customers_in_next_service(self) -> int:
        return int(round(distribution(self.service_batch_distribution, self.time_precision, is_integer=True), PRECISION)) \
            if self.is_service_batch() else 1

    def average_among_servers(self, stat: str, coef: str) -> float:
        numerator = 0
        denominator = 0
        for server in self.servers.combine_servers():
            numerator += eval(f'server.{coef}*server.{stat}')
            denominator += eval(f'server.{coef}')
        if denominator == 0:
            return 0
        return round(numerator/denominator, PRECISION)

    def initiate_service(self, customer: list[Customer], start_time: float, length_of_queue: int) -> None:
        service_duration = distribution(
            self.priority_service_distribution if customer[0].priority else self.service_distribution,
            self.time_precision
        )
        service_duration *= self.service_dependency_coefficient(length_of_queue) if self.is_service_dependent() else 1
        service = Service(start_time, start_time+service_duration, self.servers.get_server(), customer)
        self.unfinished_services.append(service)
        self.events.add(ServiceEnd(service, service.end))
        self.update_measures(situation='Service Initiation', customer_size=len(customer))
        self.update_measures(situation='Regular', time=start_time)

    def service_end(self, service: Service) -> None:
        self.servers.make_idle(service.server)
        self.unfinished_services.remove(service)
        self.update_measures(situation='Service End', service=service)
        self.update_measures(situation='Regular', time=service.end)

    def update_measures(self, **kwargs) -> None:
        match kwargs['situation']:
            case 'Regular':
                time = kwargs['time']
                for server in self.servers.combine_servers():
                    server.system_time = time
                self.average_no_of_customers = update_function(
                    self.average_no_of_customers,
                    self.last_data['time'],
                    self.last_data['number'],
                    time-self.last_data['time'],
                    time
                )
                self.last_data['time'] = time
                self.last_data['number'] = len(self)
            case 'Service Initiation':
                self.no_of_customers += kwargs['customer_size']
            case 'Service End':
                service: Service = kwargs['service']
                server = service.server
                self.no_of_customers -= len(service.customer)
                server.average_time_spent_per_customer = update_function(
                    server.average_time_spent_per_customer,
                    server.no_of_served_customers,
                    service.end-service.start,
                    len(service.customer),
                    server.no_of_served_customers+len(service.customer)
                )
                server.no_of_served_customers += len(service.customer)
                server.total_service_time = round(server.total_service_time+service.end-service.start, PRECISION)
                server.no_of_services += 1
            case 'Ending':
                time = kwargs['time']
                for service in self.unfinished_services:
                    server = service.server
                    server.average_time_spent_per_customer = update_function(
                        server.average_time_spent_per_customer,
                        server.no_of_served_customers+server.no_of_unserved_customers,
                        time - service.start,
                        len(service.customer),
                        server.no_of_served_customers+server.no_of_unserved_customers+len(service.customer)
                    )
                    server.no_of_unserved_customers += len(service.customer)
                    server.system_time = time
                    server.total_service_time += round(server.total_service_time+time-service.start, PRECISION)
                    server.no_of_unfinished_services += 1
