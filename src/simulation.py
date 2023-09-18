import numpy as np
from time import sleep
from src.system import System
from src.event import EventHeap, Arrival, Event
from src.math_utils import distribution, is_boolean_function
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
    PRECISION = 4
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
        service_dependency_stop: int = None,
        service_dependency_half: int = None,
        server_select_rand_probability: float = 0,
        priority_probability: float = 0,
        priority_service_distribution: str = None,
        bulk: bool = False,
        bulk_start: int = None,
        bulk_stop: int = None,
        bulk_half: int = None,
        renege=False,
        renege_start: int = None,
        renege_stop: int = None,
        renege_half: int = None
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
            self.PRECISION,
            self.TIME_UPDATE_UNIT
        )

    def measures(self) -> None:
        logging.info(f"system - no of finished customers: {self.system.no_of_finished_customers}")
        logging.info(f"system - all time no of customers: {self.system.all_time_no_of_customers}")
        logging.info(f"system - all time no of customers in system: {self.system.all_time_no_of_customers_system}")
        logging.info(f"system - all time no of customers in service center: {self.system.all_time_no_of_customers_service_center}")
        logging.info(f"system - all time no of customers in queue: {self.system.all_time_no_of_customers_queue}")
        logging.info(f"system - no of unfinished customers: {self.system.no_of_unfinished_customers}")
        logging.info(f"system - average no of customers: {self.system.average_no_of_customers_system}")
        logging.info(f"system - average arrival batch size: {self.system.average_arrival_batch_size}")
        logging.info(f"system - average time spent per customers: {self.system.average_time_spent_per_customer}")
        logging.info(f"system - no of arrivals: {self.system.no_of_arrivals}")
        logging.info(f"system - arrival rate: {self.system.arrival_rate}")
        logging.info(f"system - no of customers skip queue: {self.system.no_of_customers_skip_queue}")
        logging.info(f"system - proportion of customers skip queue: {self.system.proportion_of_customers_skip_queue}")
        logging.info(f"system - no of customers turned away: {self.system.no_of_customers_turned_away}")
        logging.info(f"system - proportion of customers turned away: {self.system.proportion_of_customers_turned_away}")
        logging.info(f"system - no of bulking: {self.system.no_of_bulking}")
        logging.info(f"system - proportion of bulking: {self.system.proportion_of_bulking}")
        logging.info(f"service center - no of customers: {self.system.service_center.no_of_customers}")
        logging.info(f"service center - average no of customers: {self.system.service_center.average_no_of_customers}")
        logging.info(f"service center - average service rate: {self.system.service_center.average_service_rate}")
        logging.info(f"service center - average server utilization: {self.system.service_center.average_server_utilization}")
        logging.info(f"service center - average service batch size: {self.system.service_center.average_service_batch_size}")
        logging.info(f"service center - average time spent per customer: {self.system.service_center.average_time_spent_per_customer}")
        logging.info(f"queue - no of exited customers: {self.system.queue.no_of_exited_customers}")
        logging.info(f"queue - average no of customers: {self.system.queue.average_no_of_customers}")
        logging.info(f"queue - average time spent per customer: {self.system.queue.average_time_spent_per_customer}")
        logging.info(f"queue - no of customers delayed longer {self.system.queue.t_star} star: {self.system.queue.no_of_customers_delayed_longer_t_star}")
        logging.info(f"queue - proportion of customers delayed longer {self.system.queue.t_star} star: {self.system.queue.proportion_of_customers_delayed_longer_t_star}")
        logging.info(f"queue - total time queue contains more {self.system.queue.k_star} star customers: {self.system.queue.total_time_queue_contains_more_k_star_customers}")
        logging.info(f"queue - proportion of time queue contains more {self.system.queue.k_star} star customers: {self.system.queue.proportion_of_time_queue_contains_more_k_star_customers}")
        logging.info(f"queue - no of reneging: {self.system.queue.no_of_reneging}")
        logging.info(f"queue - proportion of reneging: {self.system.queue.proportion_of_reneging}")

    def initiate_events(self):
        arrival_times = np.cumsum(
            [distribution(self.arrival_distribution, self.PRECISION) for _ in range(self.INITIAL_NO_OF_ARRIVALS)]
        )
        arrival_times_rounded = list(map(lambda t: round(t, self.PRECISION), arrival_times))
        self.events.build_heap(arrival_times_rounded)
        self.last_arrival_time = arrival_times_rounded[-1]

    def get_next_event(self):
        return self.events.pop()

    def get_peek_event(self):
        return self.events.peek()

    def add_new_arrival(self):
        new_arrival_time = round(
            self.last_arrival_time+distribution(self.arrival_distribution, self.PRECISION), self.PRECISION
        )
        self.events.add(Arrival(new_arrival_time))
        self.last_arrival_time = new_arrival_time

    def next_time(self):
        if self.speed is not None:
            sleep(self.TIME_UPDATE_UNIT*10**(-self.speed))
        return round(self.time+self.TIME_UPDATE_UNIT, self.PRECISION)

    def floored_time(self, time):
        return round(np.floor(round(time/self.TIME_UPDATE_UNIT, self.PRECISION))*self.TIME_UPDATE_UNIT, self.PRECISION)

    def is_arrival_batch(self):
        return is_boolean_function(self.arrival_batch_probability)

    def is_priority(self):
        return is_boolean_function(self.priority_probability)

    def create_customer(self, time: float) -> list[Customer]:
        no_customer_in_arrival = round(
            distribution(self.arrival_batch_distribution, self.PRECISION, integer=True), self.PRECISION
        ) if self.is_arrival_batch() else 1
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


if __name__ == '__main__':
    event_heap = EventHeap()
    s = Simulation(
        event_heap,
        2000,
        3,
        "Exponential(2)",
        "Exponential(5)",
        "FIFO",
        5,
        5,
        None,
        1000,
        0.5,
        'Discrete Uniform(1, 3)',
        0.4,
        'Discrete Uniform(1, 3)',
        False,
        None,
        None,
        None,
        0.5,
        0,
        None,
        True,
        80,
        100,
        110,
        True,
        5,
        100,
        110
    )
    s.run()
    s.measures()
