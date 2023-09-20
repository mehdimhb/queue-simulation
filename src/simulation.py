import numpy as np
from time import sleep
from src.system import System
from src.event import EventHeap, Arrival, Event
from src.math_utils import distribution, boolean_function
import logging


logging.basicConfig(
    filename='file.log', filemode='w', level=logging.DEBUG,
    format='%(asctime)s - %(filename)s - %(message)s', datefmt='%H:%M:%S'
)


class Customer:
    ID = 0

    def __init__(self, arrival_time: float, priority: bool) -> None:
        self.id = self.get_id()
        self.arrival_time = arrival_time
        self.priority = priority

    @classmethod
    def get_id(cls):
        cls.ID += 1
        return cls.ID

    def __repr__(self) -> str:
        return f"[ID:{self.id} - Arrival:{self.arrival_time} - Priority:{self.priority}]"


class Simulation:
    TIME_UPDATE_UNIT = 0.1
    TIME_PRECISION = 2
    INITIAL_NO_OF_ARRIVALS = 3

    def __init__(
        self,
        event_heap: EventHeap,
        queue_capacity: int,
        no_of_servers: int,
        arrival_distribution: str,
        service_distribution: str,
        discipline: str,
        t_star: int,
        k_star: int,
        speed: int,
        duration: int,
        arrival_batch_probability: float = 0,
        arrival_batch_distribution: str = None,
        service_batch_probability: float = 0,
        service_batch_distribution: str = None,
        service_dependency: bool = False,
        service_dependency_start: int = None,
        service_dependency_half: int = None,
        service_dependency_stop: int = None,
        server_select_rand_probability: float = 0,
        priority_probability: float = 0,
        priority_service_distribution: str = None,
        bulk: bool = False,
        bulk_start: int = None,
        bulk_half: int = None,
        bulk_stop: int = None,
        renege=False,
        renege_start: int = None,
        renege_half: int = None,
        renege_stop: int = None
    ):
        self.events = event_heap
        self.arrival_distribution = arrival_distribution
        self.arrival_batch_probability = arrival_batch_probability
        self.arrival_batch_distribution = arrival_batch_distribution
        self.priority_probability = priority_probability
        self.speed = speed
        self.duration = duration

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
            service_dependency_half,
            service_dependency_stop,
            server_select_rand_probability,
            bulk,
            bulk_start,
            bulk_half,
            bulk_stop,
            renege,
            renege_start,
            renege_half,
            renege_stop,
            discipline,
            t_star,
            k_star,
            self.TIME_PRECISION
        )

    def initiate_events(self):
        arrival_times = np.cumsum(
            [distribution(self.arrival_distribution, self.TIME_PRECISION) for _ in range(self.INITIAL_NO_OF_ARRIVALS)]
        )
        arrival_times_rounded = list(map(lambda t: round(t, self.TIME_PRECISION), arrival_times))
        self.events.build_heap(arrival_times_rounded)
        self.last_arrival_time = arrival_times_rounded[-1]

    def get_next_event(self):
        return self.events.pop()

    def get_peek_event(self):
        return self.events.peek()

    def add_new_arrival(self):
        new_arrival_time = round(
            self.last_arrival_time+distribution(self.arrival_distribution, self.TIME_PRECISION), self.TIME_PRECISION
        )
        self.events.add(Arrival(new_arrival_time))
        self.last_arrival_time = new_arrival_time

    def next_time(self):
        if self.speed is not None:
            sleep(self.TIME_UPDATE_UNIT*10**(-self.speed))
        return round(self.time+self.TIME_UPDATE_UNIT, self.TIME_PRECISION)

    def floored_time(self, time):
        return round(
            np.floor(round(time/self.TIME_UPDATE_UNIT, self.TIME_PRECISION))*self.TIME_UPDATE_UNIT, self.TIME_PRECISION
        )

    def is_arrival_batch(self):
        return boolean_function(self.arrival_batch_probability)

    def is_priority(self):
        return boolean_function(self.priority_probability)

    def create_customer(self, time: float) -> list[Customer]:
        no_customer_in_arrival = int(round(
            distribution(self.arrival_batch_distribution, self.TIME_PRECISION, is_integer=True), self.TIME_PRECISION
        )) if self.is_arrival_batch() else 1
        priority = self.is_priority()
        customer = []
        for _ in range(no_customer_in_arrival):
            customer.append(Customer(time, priority))
        return customer

    def event_manager(self, event: Event) -> None:
        if event.type == "Arrival":
            self.system.arrival(self.create_customer(event.time))
            self.add_new_arrival()
        elif event.type == "Service End":
            self.system.service_end(event)

    def update_manager(self, turn_over_time: float, ending: bool = False) -> None:
        while self.time < turn_over_time:
            self.time = self.next_time()
            self.system.update_measures(situation='Regular', time=self.time)
        if ending:
            self.system.update_measures(situation='Ending', time=self.time)
            self.time = self.next_time()

    def run(self) -> None:
        self.initiate_events()
        while self.time <= self.duration:
            event = self.get_next_event()
            if event.time > self.duration:
                self.update_manager(self.duration, ending=True)
            elif self.floored_time(event.time) == self.duration:
                self.update_manager(self.duration)
                self.event_manager(event)
                if self.get_peek_event().time > self.duration:
                    self.update_manager(self.duration, ending=True)
            elif self.floored_time(event.time) == self.time:
                self.event_manager(event)
            else:
                self.update_manager(self.floored_time(event.time))
                self.event_manager(event)
