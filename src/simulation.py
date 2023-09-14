import numpy as np
from time import sleep
from numbers import Number
from system import System
from event import EventHeap, Arrival
from math_utils import distribution


class Customer:
    def __init__(self, id: int, arrival_time: float, priority: bool) -> None:
        self.id = id
        self.arrival_time = arrival_time
        self.priority = priority

    def __repr__(self) -> str:
        return f"[ID:{self.id} - Arrival:{self.arrival_time} - Priority:{self.priority}]"


class Simulation:
    def __init__(
        self,
        event_heap: EventHeap,
        queue_capacity=100,
        no_of_servers=2,
        arrival_distribution='cont-uniform(0.1, 0.6)',
        arrival_batch_probability=0.5,
        arrival_batch_distribution='disc-uniform(2, 4)',
        service_distribution='normal(1, 1)',
        service_batch_probability=0,
        service_batch_distribution='disc-uniform(2, 4)',
        service_dependency=False,
        service_dependency_start=50,
        service_dependency_stop=250,
        service_dependency_half=150,
        server_select_rand_probability=0,
        priority_probability=0.5,
        priority_service_distribution='normal(0.5, 1)',
        bulk=False,
        bulk_start=50,
        bulk_stop=500,
        bulk_half=250,
        renege=False,
        renege_start=50,
        renege_stop=500,
        renege_half=250,
        discipline='FIFO',
        t_star=10,
        k_star=10,
        speed=2,
        duration=20
    ):
        self.events = event_heap
        self.arrival_distribution = arrival_distribution
        self.arrival_batch_probability = arrival_batch_probability
        self.arrival_batch_distribution = arrival_batch_distribution
        self.priority_probability = priority_probability
        self.speed = speed
        self.duration = duration

        self._time_update_unit = 0.1
        self._precision = 4
        self._is_paused = False
        self._initial_no_of_arrivals = 3

        self.no_of_customers = 0
        self.arrival_rate = 0

        self.time = 0
        self.last_arrival_time = 0
        self.system = System(
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
            self.precision,
            self.time_update_unit
        )

    @property
    def time_update_unit(self):
        return self._time_update_unit

    @time_update_unit.setter
    def time_update_unit(self, value):
        if not isinstance(value, Number):
            raise ValueError("Time update unit must be a number")
        if value <= 0:
            raise ValueError("Time update unit cannot be a non-positive")
        self._time_update_unit = value

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, value):
        if not isinstance(value, int):
            raise ValueError("Precision must be an integer")
        if value < 0:
            raise ValueError("Precision cannot be negative")
        self._precision = value

    @property
    def is_paused(self):
        return self._is_paused

    @is_paused.setter
    def is_paused(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_paused must be a boolean")
        self._is_paused = value

    @property
    def initial_no_of_arrivals(self):
        return self._initial_no_of_arrivals

    @initial_no_of_arrivals.setter
    def initial_no_of_arrivals(self, value):
        if not isinstance(value, int):
            raise ValueError("Initial number of arrivals must be an integer")
        if value < 0:
            raise ValueError("Initial number of arrivals cannot be negative")
        self._initial_no_of_arrivals = value

    def initiate_events(self):
        arrival_times = np.cumsum([distribution(self.arrival_distribution) for _ in range(self.initial_no_of_arrivals)])
        arrival_times_rounded = list(map(lambda t: round(t, self.precision), arrival_times))
        self.initial_no_of_arrivals
        self.events.build_heap(arrival_times_rounded)
        self.last_arrival_time = arrival_times_rounded[-1]

    def get_next_event(self):
        return self.events.pop()

    def add_new_arrival(self):
        new_arrival_time = round(self.last_arrival_time+distribution(self.arrival_distribution), self.precision)
        self.events.add(Arrival(new_arrival_time))
        self.last_arrival_time = new_arrival_time

    def next_time(self):
        if not self.is_paused:
            sleep(self.time_update_unit*10**(-self.speed))
            return round(self.time+self.time_update_unit, self.precision)

    def floored_time(self, time):
        return round(np.floor(round(time/self.time_update_unit, self.precision))*self.time_update_unit, self.precision)

    def is_arrival_batch(self):
        return bool(np.random.choice(2, p=[1-self.arrival_batch_probability, self.arrival_batch_probability]))

    def is_priority(self):
        return bool(np.random.choice(2, p=[1-self.priority_probability, self.priority_probability]))

    def create_customer(self, time: float) -> list[Customer]:
        no_customer_in_arrival = round(distribution(self.arrival_batch_distribution, condition=1), self.precision) \
            if self.is_arrival_batch() else 1
        priority = self.is_priority()
        customer = []
        for _ in range(no_customer_in_arrival):
            self.no_of_customers += 1
            customer.append(Customer(self.no_of_customers, time, priority))
        return customer

    def update_measures(self) -> None:
        self.arrival_rate = self.no_of_customers/self.time
        self.system.update_measures(self.time)

    def event_manager(self, event):
        if event.type == "Arrival":
            self.system.arrival(self.create_customer(event.time))
            self.add_new_arrival()
        elif event.type == "Service End":
            self.system.service_end(event)

    def regular_manager(self, turn_over_time):
        while self.time < turn_over_time:
            self.time = self.next_time()
            self.update_measures()

    def run(self):
        self.initiate_events()
        while self.time < self.duration:
            event = self.get_next_event()
            if self.floored_time(event.time) == self.time:
                self.event_manager(event)
            elif event.time > self.duration:
                self.regular_manager(self.duration)
            else:
                self.regular_manager(self.floored_time(event.time))
                self.event_manager(event)


if __name__ == "__main__":
    event_heap = EventHeap()
    s = Simulation(event_heap)
    s.run()
