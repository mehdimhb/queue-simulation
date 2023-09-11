import numpy as np
from time import sleep
from numbers import Number
from system import System
from event import EventHeap
from distributions import distribution
import logging

logging.basicConfig(
    filename='file.log', filemode='w', level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S'
)


class Customer:
    def __init__(self, id, arrival_time, priority):
        self.id = id
        self.arrival_time = arrival_time
        self.priority = priority

    def __repr__(self):
        return f"[ID:{self.id} - Arrival:{self.arrival_time} - Priority:{self.priority}]"


class Simulation:
    def __init__(
        self,
        queue_capacity=np.inf,
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
        speed=1,
        duration=3
    ):
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

        self.time = 0
        self.last_arrival_time = 0
        self.no_of_customer = 0
        self.events = EventHeap()
        """
        self.system = System(
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
        )"""

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
            raise ValueError("Initial number of customers must be an integer")
        if value < 0:
            raise ValueError("Initial number of customers cannot be negative")
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
        self.events.add("Arrival", new_arrival_time)
        logging.debug(f"in add_new_arrival: {self.time}")
        logging.debug(f"new time: {new_arrival_time}")
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

    def create_customer(self, time):
        logging.debug(f"enter create customer: {self.time}")
        logging.debug(f"starting no of customers: {self.no_of_customer}")
        no_customer_in_arrival = 1
        if self.is_arrival_batch():
            no_customer_in_arrival = round(distribution(self.arrival_batch_distribution, condition=1), self.precision)
        priority = self.is_priority()
        customer = []
        for _ in range(no_customer_in_arrival):
            self.no_of_customer += 1
            customer.append(Customer(self.no_of_customer, time, priority))
        logging.debug(f"ending no of customers: {self.no_of_customer}")
        return customer

    def event_manager(self, event):
        logging.debug(f"enter event manager: {self.time}")
        if event.type == "Arrival":
            logging.debug(f"enter arrival: {self.time}")
            customer = self.create_customer(event.time)
            logging.debug(f"customer created: {customer}")
            #self.system.arrival(self.create_customer(event.time))
            self.add_new_arrival()
            logging.debug(f"added new arrival: {self.events}")
            #self.system.update_measures()
            logging.debug(f"update for: {self.time}")
        elif event.type == "Service End":
            pass
            #self.system.service_end(event.time)

    def regular_manager(self, turn_over_time):
        logging.debug(f"enter regular manager: {self.time}")
        while self.time < turn_over_time:
            logging.debug(f"beginning of regular while: {self.time}")
            self.time = self.next_time()
            logging.debug(f"time changed: {self.time}")
            #self.system.update_measures()
            logging.debug(f"update for: {self.time}")

    def run(self):
        logging.debug(f"simulation begin: {self.time}")
        # self.initiate_events()
        self.events.build_heap([0.15, 0.15, 0.3, 0.3, 0.3, 0.55])
        self.last_arrival_time = 0.55
        logging.debug(f"initial events: {self.events}")
        while self.time < self.duration:
            logging.debug(f"beginning of while: {self.time}")
            event = self.get_next_event()
            logging.debug(f"get next event: {event}")
            if self.floored_time(event.time) == self.time:
                logging.debug(f"enter event.time == self.time: {self.time}")
                self.event_manager(event)
                logging.debug(f"exit event manager: {self.time}")
            elif event.time > self.duration:
                logging.debug(f"enter event.time > self.duration: {self.time}")
                self.regular_manager(self.duration)
                logging.debug(f"exit regular manager: {self.time}")
            else:
                logging.debug(f"enter else: {self.time}")
                self.regular_manager(self.floored_time(event.time))
                logging.debug(f"exit regular manager: {self.time}")
                self.event_manager(event)
                logging.debug(f"exit event manager: {self.time}")
            logging.debug(f"end of while: {self.time}")
        logging.debug(f"end of simulation: {self.time}")


if __name__ == "__main__":
    s = Simulation()
    s.run()
