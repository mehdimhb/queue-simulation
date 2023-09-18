from __future__ import annotations
import numpy as np
from src.math_utils import update_function, is_boolean_function, logistic
from typing import Iterator, TYPE_CHECKING
if TYPE_CHECKING:
    from src.simulation import Customer


class Queue:
    def __init__(
        self,
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
    ):
        self.queue_capacity = queue_capacity
        self.server_select_rand_probability = server_select_rand_probability
        self.renege = renege
        self.renege_start = renege_start
        self.renege_stop = renege_stop
        self.renege_half = renege_half
        self.t_star = t_star
        self.k_star = k_star
        self.discipline = discipline
        self.precision = precision
        self.time_update_unit = time_update_unit

        self.no_of_exited_customers = 0
        self.average_no_of_customers = 0
        self.average_time_spent_per_customer = 0
        self.no_of_customers_delayed_longer_t_star = 0
        self.total_time_queue_contains_more_k_star_customers = 0
        self.no_of_reneging = 0

        self.last_data = {'time': 0, 'number': 0}
        self.regular_queue: list[Customer] = []
        self.priority_queue: list[Customer] = []

    @property
    def proportion_of_customers_delayed_longer_t_star(self):
        if self.no_of_exited_customers == 0:
            return 0
        return self.no_of_customers_delayed_longer_t_star/self.no_of_exited_customers

    @property
    def proportion_of_time_queue_contains_more_k_star_customers(self):
        if self.last_data['time'] == 0:
            return 0
        return self.total_time_queue_contains_more_k_star_customers/self.last_data['time']

    @property
    def proportion_of_reneging(self):
        if self.no_of_exited_customers == 0:
            return 0
        return self.no_of_reneging/self.no_of_exited_customers

    def __len__(self) -> int:
        return len(self.regular_queue)+len(self.priority_queue)

    def combine_queue(self) -> list[Customer]:
        combination = self.regular_queue[:]
        combination.extend(self.priority_queue)
        return combination

    def remaining_capacity(self) -> int:
        return self.queue_capacity-len(self) if not self.is_full() else 0

    def is_full(self) -> bool:
        return len(self) == self.queue_capacity

    def is_empty(self) -> bool:
        return len(self) == 0

    def is_next_service_random(self) -> bool:
        return is_boolean_function(self.server_select_rand_probability)

    def is_renege(self, delaying_time: float) -> bool:
        probability = logistic(delaying_time, self.renege_start, self.renege_stop, self.renege_half)
        return is_boolean_function(probability)

    def join(self, customers: list[Customer]) -> None:
        for customer in customers:
            if customer.priority:
                self.priority_queue.append(customer)
            else:
                match self.discipline:
                    case 'FIFO':
                        self.regular_queue.append(customer)
                    case 'LIFO':
                        self.regular_queue.insert(0, customer)
                    case 'SIRO':
                        i = np.random.randint(len(self.regular_queue)+1)
                        self.regular_queue.insert(i, customer)
        self.update_measures(situation='Regular', time=customers[0].arrival_time)

    def pop(self, no_of_customers: int) -> Iterator[Customer]:
        for _ in range(no_of_customers):
            if self.is_next_service_random():
                i = np.random.randint(len(self))
                yield self.combine_queue().pop(i)
            if self.priority_queue:
                yield self.priority_queue.pop(0)
            else:
                yield self.regular_queue.pop(0)

    def update_measures(self, **kwargs):
        match kwargs['situation']:
            case 'Regular':
                time = kwargs['time']
                self.average_no_of_customers = update_function(
                    self.average_no_of_customers,
                    self.last_data['time'],
                    self.last_data['number'],
                    time-self.last_data['time'],
                    time
                )
                self.total_time_queue_contains_more_k_star_customers += \
                    time-self.last_data['time'] if self.k_star <= self.last_data['number'] else 0
                if self.renege:
                    self.reneging(time)
                self.last_data['time'] = time
                self.last_data['number'] = len(self)
            case 'Pop':
                arrival_time = kwargs['arrival_time']
                exit_time = kwargs['exit_time']
                self.average_time_spent_per_customer = update_function(
                    self.average_time_spent_per_customer,
                    self.no_of_exited_customers,
                    exit_time-arrival_time,
                    1,
                    self.no_of_exited_customers+1
                )
                self.no_of_exited_customers += 1
                self.no_of_customers_delayed_longer_t_star += 1 if self.t_star <= exit_time-arrival_time else 0
            case 'Reneging':
                self.no_of_reneging += 1
            case 'Ending':
                time = kwargs['time']
                for i, customer in enumerate(self.combine_queue()):
                    self.average_time_spent_per_customer = update_function(
                        self.average_time_spent_per_customer,
                        self.no_of_exited_customers+i,
                        time - customer.arrival_time,
                        1,
                        self.no_of_exited_customers+i+1
                    )
                    self.no_of_customers_delayed_longer_t_star += 1 if self.t_star <= time-customer.arrival_time else 0

    def reneging(self, time: float) -> None:
        for customer in self.regular_queue:
            if self.is_renege(time - customer.arrival_time):
                self.regular_queue.remove(customer)
                self.update_measures(situation='Reneging')
                self.update_measures(situation='Pop', arrival_time=customer.arrival_time, exit_time=time)
