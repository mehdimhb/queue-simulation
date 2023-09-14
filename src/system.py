from __future__ import annotations
from service_center import ServiceCenter
from queue_management import Queue
from math_utils import update_function, logistic, is_boolean_function
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from simulation import Customer
    from service_center import Service
    from event import ServiceEnd


class System:
    def __init__(
        self,
        event_heap,
        queue_capacity,
        no_of_servers,
        service_distribution,
        priority_service_distribution,
        service_batch_probability,
        service_batch_distribution,
        service_dependency,
        service_dependency_start,
        service_dependency_stop,
        service_dependency_half,
        server_select_rand_probability,
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
        k_star,
        precision,
        time_update_unit
    ):
        self.bulk = bulk
        self.bulk_start = bulk_start
        self.bulk_stop = bulk_stop
        self.bulk_half = bulk_half

        self.all_time_no_of_customers = 0
        self.average_no_of_customers = 0
        self.average_time_spent_per_customer = 0
        self.effective_arrival_rate = 0
        self.no_of_customers_skip_queue = 0
        self.proportion_of_customers_skip_queue = 0
        self.no_of_customers_turned_away = 0
        self.proportion_of_customers_turned_away = 0
        self.last_time_length = (0, 0)

        self.service_center = ServiceCenter(
            event_heap,
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
        )
        self.queue = Queue(
            queue_capacity,
            server_select_rand_probability,
            renege,
            renege_start,
            renege_stop,
            renege_half,
            t_star,
            k_star,
            discipline,
            precision,
            time_update_unit
        )

    def __len__(self) -> int:
        return len(self.queue) + len(self.service_center)

    def is_bulk(self, length_of_queue: int) -> bool:
        if not self.bulk:
            return False
        probability = logistic(length_of_queue, self.bulk_start, self.bulk_stop, self.bulk_half)
        return is_boolean_function(probability)

    def arrival(self, customer: list[Customer]) -> None:
        initial_no_of_customers = len(customer)
        if not self.service_center.is_full():
            for _ in range(self.service_center.remaining_capacity()):
                if customer:
                    self.no_of_customers_skip_queue += len(customer)
                    customer = self.join_service_center_manager(customer)
        if not self.queue.is_full() and not self.is_bulk(len(self.queue)):
            customer = self.join_queue_manager(customer)
        if customer:
            self.no_of_customers_turned_away += len(customer)
        self.all_time_no_of_customers += initial_no_of_customers - len(customer)

    def join_service_center_manager(self, customer: list[Customer]) -> list[Customer]:
        no_customers_in_next_service = self.service_center.no_of_customers_in_next_service()
        customers_go_to_service_center = customer[:no_customers_in_next_service]
        self.service_center.initiate_service(
                customer=customers_go_to_service_center,
                start_time=customers_go_to_service_center[0].arrival_time,
                length_of_queue=len(self.queue)
            )
        self.update_measures(customer[0].arrival_time)
        return customer[no_customers_in_next_service:]

    def join_queue_manager(self, customer: list[Customer]) -> list[Customer]:
        queue_remaining_capacity = self.queue.remaining_capacity()
        self.queue.join(customer[:queue_remaining_capacity])
        self.update_measures(customer[0].arrival_time)
        return customer[queue_remaining_capacity:]

    def service_end(self, event: ServiceEnd) -> None:
        self.service_center.service_end(event.service)
        self.update_measures("service end", event.service.customer)
        customer = self.queue.pop(self.service_center.no_of_customers_in_next_service())
        self.service_center.initiate_service(
            customer=customer,
            start_time=event.service.end,
            length_of_queue=len(self.queue)
        )
        self.update_measures(event.service.end, service=event.service)

    def update_measures(self, time: float, service: Service = None) -> None:
        self.average_no_of_customers = update_function(
            self.average_no_of_customers,
            self.last_time_length[0],
            self.last_time_length[1],
            time-self.last_time_length[0],
            time
        )
        self.effective_arrival_rate = self.all_time_no_of_customers/time
        if self.all_time_no_of_customers:
            self.average_time_spent_per_customer = update_function(
                self.service_center.average_time_spent_per_customer,
                self.service_center.all_time_no_customers,
                self.queue.average_time_spent_per_customer,
                self.queue.all_time_no_of_customers,
                self.all_time_no_of_customers
            )
            self.proportion_of_customers_skip_queue = self.no_of_customers_skip_queue/self.all_time_no_of_customers
            self.proportion_of_customers_turned_away = self.no_of_customers_turned_away/self.all_time_no_of_customers
        self.last_time_length = (time, len(self))
        self.service_center.update_measure(time, service=service)
        self.queue.update_measures(time)
