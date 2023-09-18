from __future__ import annotations
from src.service_center import ServiceCenter
from src.queue_management import Queue
from src.math_utils import update_function, logistic, is_boolean_function
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from src.simulation import Customer
    from src.service_center import Service
    from src.event import ServiceEnd
import logging


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

        self.no_of_finished_customers = 0
        self.all_time_no_of_customers = 0
        self.all_time_no_of_customers_system = 0
        self.all_time_no_of_customers_service_center = 0
        self.all_time_no_of_customers_queue = 0
        self.no_of_unfinished_customers = 0

        self.average_no_of_customers_system = 0
        self.average_time_spent_per_customer = 0

        self.no_of_arrivals = 0
        self.no_of_customers_skip_queue = 0
        self.no_of_customers_turned_away = 0
        self.no_of_bulking = 0

        self.last_data = {'time': 0, 'number': 0}

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

    @property
    def average_arrival_batch_size(self):
        if self.no_of_arrivals == 0:
            return 0
        return self.all_time_no_of_customers/self.no_of_arrivals

    @property
    def arrival_rate(self):
        if self.last_data['time'] == 0:
            return 0
        return self.no_of_arrivals/self.last_data['time']

    @property
    def proportion_of_customers_skip_queue(self):
        if self.all_time_no_of_customers_system == 0:
            return 0
        return self.no_of_customers_skip_queue/self.all_time_no_of_customers_system

    @property
    def proportion_of_customers_turned_away(self):
        if self.all_time_no_of_customers == 0:
            return 0
        return self.no_of_customers_turned_away/self.all_time_no_of_customers

    @property
    def proportion_of_bulking(self):
        if self.all_time_no_of_customers == 0:
            return 0
        return self.no_of_bulking/self.all_time_no_of_customers

    def __len__(self) -> int:
        return len(self.queue) + len(self.service_center)

    def is_bulk(self) -> bool:
        if not self.bulk:
            return False
        probability = logistic(len(self.queue), self.bulk_start, self.bulk_stop, self.bulk_half)
        logging.debug(f'probability = {probability} - length={len(self.queue)}')
        return is_boolean_function(probability)

    def arrival(self, customer: list[Customer]) -> None:
        self.update_measures(situation='Arrival', customer_size=len(customer))
        if not self.service_center.is_full():
            for _ in range(self.service_center.remaining_capacity()):
                if customer:
                    customer = self.join_service_center_manager(customer)
        if customer and not self.queue.is_full():
            if self.is_bulk():
                self.update_measures(situation='Bulk', customer_size=len(customer))
            else:
                customer = self.join_queue_manager(customer)
        if customer:
            self.update_measures(situation='Turned Away', customer_size=len(customer))

    def join_service_center_manager(self, customer: list[Customer]) -> list[Customer]:
        no_customers_in_next_service = self.service_center.no_of_customers_in_next_service()
        customers_join_service_center = customer[:no_customers_in_next_service]
        self.service_center.initiate_service(
                customer=customers_join_service_center,
                start_time=customers_join_service_center[0].arrival_time,
                length_of_queue=len(self.queue)
            )
        self.update_measures(situation='Join Service Center', customer_size=len(customers_join_service_center))
        self.update_measures(situation='Skip Queue', customer_size=len(customers_join_service_center))
        self.update_measures(situation='Regular', time=customer[0].arrival_time)
        return customer[no_customers_in_next_service:]

    def join_queue_manager(self, customer: list[Customer]) -> list[Customer]:
        queue_remaining_capacity = self.queue.remaining_capacity()
        self.queue.join(customer[:queue_remaining_capacity])
        self.update_measures(situation='Join Queue', customer_size=len(customer[:queue_remaining_capacity]))
        self.update_measures(situation='Regular', time=customer[0].arrival_time)
        return customer[queue_remaining_capacity:]

    def service_end(self, event: ServiceEnd) -> None:
        self.service_center.service_end(event.service)
        if not self.queue.is_empty():
            customers = list(self.queue.pop(self.service_center.no_of_customers_in_next_service()))
            for customer in customers:
                self.queue.update_measures(situation='Pop', arrival_time=customer.arrival_time, exit_time=event.service.end)
            self.queue.update_measures(situation='Regular', time=event.service.end)
            self.service_center.initiate_service(
                customer=customers,
                start_time=event.service.end,
                length_of_queue=len(self.queue)
            )
            self.update_measures(situation='Join Service Center', customer_size=len(customers))
        for customer in event.service.customer:
            self.update_measures(
                situation='Service End', service_end=event.service.end, customer_arrival=customer.arrival_time
            )
        self.update_measures(situation='Regular', time=event.service.end)

    def update_measures(self, **kwargs: Any) -> None:
        match kwargs['situation']:
            case 'Regular':
                time = kwargs['time']
                self.average_no_of_customers_system = update_function(
                    self.average_no_of_customers_system,
                    self.last_data['time'],
                    self.last_data['number'],
                    time-self.last_data['time'],
                    time
                )
                self.last_data['time'] = time
                self.last_data['number'] = len(self)
                self.service_center.update_measures(situation='Regular', time=time)
                self.queue.update_measures(situation='Regular', time=time)
            case 'Arrival':
                self.no_of_arrivals += 1
                self.all_time_no_of_customers += kwargs['customer_size']
                self.all_time_no_of_customers_system += kwargs['customer_size']
            case 'Join Service Center':
                self.all_time_no_of_customers_service_center += kwargs['customer_size']
            case 'Skip Queue':
                self.no_of_customers_skip_queue += kwargs['customer_size']
            case 'Join Queue':
                self.all_time_no_of_customers_queue += kwargs['customer_size']
            case 'Bulk':
                self.no_of_bulking += kwargs['customer_size']
            case 'Turned Away':
                self.all_time_no_of_customers_system -= kwargs['customer_size']
                self.no_of_customers_turned_away += kwargs['customer_size']
            case 'Service End':
                self.average_time_spent_per_customer = update_function(
                    self.average_time_spent_per_customer,
                    self.no_of_finished_customers,
                    kwargs['service_end'] - kwargs['customer_arrival'],
                    1,
                    self.no_of_finished_customers+1
                )
                self.no_of_finished_customers += 1
            case 'Ending':
                time = kwargs['time']
                customers = self.queue.combine_queue()
                customers.extend([customer
                                  for service in self.service_center.unfinished_services
                                  for customer in service.customer])
                for customer in customers:
                    self.average_time_spent_per_customer = update_function(
                        self.average_time_spent_per_customer,
                        self.no_of_finished_customers+self.no_of_unfinished_customers,
                        time - customer.arrival_time,
                        1,
                        self.no_of_finished_customers+self.no_of_unfinished_customers+1
                    )
                    self.no_of_unfinished_customers += 1
                self.service_center.update_measures(situation='Ending', time=time)
                self.queue.update_measures(situation='Ending', time=time)
