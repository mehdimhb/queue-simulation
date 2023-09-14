from __future__ import annotations
import numpy as np
from math_utils import update_function, is_boolean_function, logistic
from typing import Iterator, TYPE_CHECKING
if TYPE_CHECKING:
    from simulation import Customer


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

        # statistics
        self.all_time_no_of_customers = 0
        self.average_no_of_customers = 0
        self.average_time_spent_per_customer = 0
        self.no_of_customers_delayed_longer_t_star = 0
        self.proportion_of_customers_delayed_longer_t_star = 0
        self.awaiting_customers_delayed_longer_t_star = []
        self.total_time_queue_contains_more_k_star_customers = 0
        self.proportion_of_time_queue_contains_more_k_star_customers = 0
        self.last_time_length = (0, 0)

        self.regular_queue = []
        self.priority_queue = []

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

    def is_next_service_random(self) -> bool:
        return is_boolean_function(self.server_select_rand_probability)

    def is_renege(self, delaying_time: float) -> bool:
        if not self.renege:
            return False
        probability = logistic(delaying_time, self.renege_start, self.renege_stop, self.renege_half)
        return is_boolean_function(probability)

    def join(self, customers: list[Customer]) -> None:
        for customer in customers:
            self.all_time_no_of_customers += 1
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

    def pop(self, no_of_customers: int) -> Iterator[Customer]:
        for _ in range(no_of_customers):
            if self.is_next_service_random():
                i = np.random.randint(len(self)+1)
                yield self.combine_queue().pop(i)
            if self.priority_queue:
                yield self.priority_queue.pop(0)
            else:
                yield self.regular_queue.pop(0)

    def update_measures(self, time: float) -> None:
        self.reneging(time)
        self.average_no_of_customers = update_function(
            self.average_no_of_customers,
            self.last_time_length[0],
            self.last_time_length[1],
            time-self.last_time_length[0],
            time
        )
        average_time_spent_in_queue_right_now = self.update_by_iterating_on_queue(time)
        self.average_time_spent_per_customer = update_function(
            self.average_time_spent_per_customer,
            self.last_time_length[0],
            average_time_spent_in_queue_right_now,
            time-self.last_time_length[0],
            time
        )
        if self.all_time_no_of_customers:
            self.proportion_of_customers_delayed_longer_t_star = \
                self.no_of_customers_delayed_longer_t_star/self.all_time_no_of_customers
        self.total_time_queue_contains_more_k_star_customers += \
            0 if self.last_time_length[1] < self.k_star else time-self.last_time_length[0]
        self.proportion_of_time_queue_contains_more_k_star_customers = \
            self.total_time_queue_contains_more_k_star_customers/time
        self.reneging(time)
        self.last_time_length = (time, len(self))

    def update_by_iterating_on_queue(self, time: float) -> float:
        time_spent = 0
        for customer in self.combine_queue():
            time_spent += time - customer.arrival_time
            if self.t_star <= customer.arrival_time and \
                    customer not in self.awaiting_customers_delayed_longer_t_star:
                self.no_of_customers_delayed_longer_t_star += 1
                self.awaiting_customers_delayed_longer_t_star.append(customer)
        return round(time_spent/time, self.precision)

    def reneging(self, time: float) -> None:
        for customer in self.regular_queue:
            if self.is_renege(time - customer.arrival_time):
                self.regular_queue.remove(customer)
