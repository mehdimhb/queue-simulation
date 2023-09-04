import numpy as np
from scipy.stats import norm  # , poisson
import re
import time
from server import Server
from customer import Customer


class Queue:
    def __init__(
        self,
        queue_capacity=np.inf,
        number_of_servers=2,
        arrival_disturbution='exponential(0.5)',
        arrival_in_batches_probability=0,
        batch_size_disturbution='uniform(2, 4)',
        priority_probability=0.5,
        priority_service_disturbution='normal(0.5, 1)',
        service_disturbution='normal(1, 1)',
        service_to_batch_probability=0,
        service_batch_size_disturbution='uniform(2, 4)',
        is_service_depend_on_queue_length=False,
        length_queue_when_service_time_became_half=150,
        service_dependance_start=50,
        service_dependance_stop=250,
        server_choose_randomly_probability=0,
        bulk=False,
        bulk_start=50,
        bulk_stop=500,
        bulk_half=250,
        renege=False,
        renege_start=50,
        renege_stop=500,
        renege_half=250,
        discipline='FIFO',
        t0=10,
        k0=10,
        time_speed=0,
        only_first_and_last=True,
        number_of_unit_of_time_for_simulation=1000
    ):
        # system properties
        self.queue_capacity = queue_capacity
        self.number_of_servers = number_of_servers

        # arrival properties
        self.arrival_disturbution = arrival_disturbution
        self.arrival_in_batches_probability = arrival_in_batches_probability
        self.batch_size_disturbution = batch_size_disturbution
        self.priority_probability = priority_probability
        self.priority_service_disturbution = priority_service_disturbution

        # service properties
        self.service_disturbution = service_disturbution
        self.service_to_batch_probability = service_to_batch_probability
        self.service_batch_size_disturbution = service_batch_size_disturbution
        self.server_choose_randomly_probability = server_choose_randomly_probability
        self.is_service_depend_on_queue_length = is_service_depend_on_queue_length
        self.length_queue_when_service_time_became_half = length_queue_when_service_time_became_half
        self.service_dependance_start = service_dependance_start
        self.service_dependance_stop = service_dependance_stop

        # queue behavior and disciline
        self.bulk = bulk
        self.bulk_start = bulk_start
        self.bulk_stop = bulk_stop
        self.bulk_half = bulk_half
        self.renege = renege
        self.renege_start = renege_start
        self.renege_stop = renege_stop
        self.renege_half = renege_half
        self.discipline = discipline

        # measures of performance
        self.time = 0
        self.time_speed = time_speed
        self.time_unit_update = 0.1
        self.is_paused = False
        self.arrival_rate = 0
        self.effective_arrival_rate = 0
        self.average_service_rate = 0

        self.total_number_of_customers = 0
        self.total_number_of_customers_go_direct_to_server = 0
        self.proportion_of_customers_go_direct_to_server = 0
        self.number_of_customers_in_system_at_t = 0
        self.number_of_customers_in_queue_at_t = 0
        self.last_time_number_customer_system_changed = 0
        self.last_time_number_customer_queue_changed = 0
        self.average_number_of_customers_in_system = 0
        self.average_number_of_customers_in_queue = 0
        self.total_time_spent_in_system_all_customers = 0
        self.total_time_spent_in_queue_all_customers = 0
        self.total_time_spent_in_system_all_customers_definitive = 0
        self.total_time_spent_in_queue_all_customers_definitive = 0
        self.average_time_spent_in_system_per_customer = 0
        self.average_time_spent_in_queue_per_customer = 0
        self.number_of_busy_servers_at_t = 0
        self.average_server_utilization = 0

        self.t0 = t0
        self.customers_in_queue_with_t0_counted = []
        self.number_of_customers_delayed_in_queue_longer_than_t0_time = 0
        self.proportion_of_customers_delayed_in_queue_longer_than_t0_time = 0
        self.k0 = k0
        self.times_queue_contains_more_than_k0_customers = 0
        self.last_time_queue_k0 = 0
        self.queue_is_k0 = False
        self.proportion_of_time_queue_contains_more_than_k0_customers = 0
        self.number_of_customers_turned_away = 0
        self.proportion_of_customers_turned_away = 0
        
        self.only_first_and_last = only_first_and_last
        self.number_of_unit_of_time_for_simulation = number_of_unit_of_time_for_simulation
        
        self.queue = []
        self.servers = [Server(i) for i in range(self.number_of_servers)]
        self.arrivals = list(map(lambda a: round(a, 2), np.cumsum([self.disturbution(self.arrival_disturbution) for _ in range(100)])))
        self.events = self.arrivals[:]

    def __str__(self):
        qq = [str(x) for x in self.queue]
        s = [str(x) for x in self.servers]
        ss = [(x.id, x.service_rate) for x in self.servers]
        sss = [(x.id, x.server_utilization) for x in self.servers]
        s3 = [(x.id, x.total_time_of_service_definitive) for x in self.servers]
        s4 = [(x.id, x.total_time_of_service) for x in self.servers]
        s5 = [(x.id, x.total_number_of_served_customer) for x in self.servers]
        return f"""total_number_of_customers = {self.total_number_of_customers}
        arrival_rate = {self.arrival_rate}
        effective_arrival_rate = {self.effective_arrival_rate}
        number_of_busy_servers_at_t = {self.number_of_busy_servers_at_t}
        total_time_of_services_definitive = {s3}
        total_time_of_services = {s4}
        total_number_of_served_customer = {s5}
        service_rate = {ss}
        average_service_rate = {self.average_service_rate}
        server_utilization = {sss}
        average_server_utilization = {self.average_server_utilization}
        total_number_of_customers_go_direct_to_server = {self.total_number_of_customers_go_direct_to_server}
        proportion_of_customers_go_direct_to_server = {self.proportion_of_customers_go_direct_to_server}
        number_of_customers_in_system_at_t = {self.number_of_customers_in_system_at_t}
        number_of_customers_in_queue_at_t = {self.number_of_customers_in_queue_at_t}
        average_number_of_customers_in_system = {self.average_number_of_customers_in_system}
        average_number_of_customers_in_queue = {self.average_number_of_customers_in_queue}
        total_time_spent_in_system_per_customer = {self.total_time_spent_in_system_all_customers}
        total_time_spent_in_queue_per_customer = {self.total_time_spent_in_queue_all_customers}
        total_time_spent_in_system_all_customers_definitive = {self.total_time_spent_in_system_all_customers_definitive}
        total_time_spent_in_queue_all_customers_definitive = {self.total_time_spent_in_queue_all_customers_definitive}
        average_time_spent_in_system_per_customer = {self.average_time_spent_in_system_per_customer}
        average_time_spent_in_queue_per_customer = {self.average_time_spent_in_queue_per_customer}
        number_of_customers_delayed_in_queue_longer_than_{self.t0}_time = {self.number_of_customers_delayed_in_queue_longer_than_t0_time}
        proportion_of_customers_delayed_in_queue_longer_than_{self.t0}_time = {self.proportion_of_customers_delayed_in_queue_longer_than_t0_time}
        times_queue_contains_more_than_{self.k0}_customers = {self.times_queue_contains_more_than_k0_customers}
        proportion_of_time_queue_contains_more_than_{self.k0}_customers = {self.proportion_of_time_queue_contains_more_than_k0_customers}
        number_of_customers_turned_away = {self.number_of_customers_turned_away}
        proportion_of_customers_turned_away = {self.proportion_of_customers_turned_away}
        queue = {qq}
        servers = {s}"""

    def average_number_of_customers_in_system_update(self):
        if not self.time:
            return 0
        return round(self.average_number_of_customers_in_system*(self.last_time_number_customer_system_changed/self.time)+\
            (self.time - self.last_time_number_customer_system_changed)*self.number_of_customers_in_system_at_t/self.time, 2)

    def average_number_of_customers_in_queue_update(self):
        if not self.time:
            return 0
        return round(self.average_number_of_customers_in_queue*(self.last_time_number_customer_queue_changed/self.time)+\
            (self.time - self.last_time_number_customer_queue_changed)*self.number_of_customers_in_queue_at_t/self.time, 2)

    def customer_arrival_failure_update(self):
        self.number_of_customers_turned_away += 1
        self.total_number_of_customers += 1
        self.proportion_of_customers_turned_away = round(self.number_of_customers_turned_away/self.total_number_of_customers, 2)

    def customer_arrival_succeed_update(self, n=1):
        self.total_number_of_customers += n
        self.average_number_of_customers_in_system = self.average_number_of_customers_in_system_update()
        self.last_time_number_customer_system_changed = self.time
        self.number_of_customers_in_system_at_t += n

    def customer_join_queue_update(self):
        self.average_number_of_customers_in_queue = self.average_number_of_customers_in_queue_update()
        self.last_time_number_customer_queue_changed = self.time
        self.number_of_customers_in_queue_at_t += 1

    def customer_receive_service_update(self, customers, direct=False):
        self.number_of_busy_servers_at_t += 1
        for customer in customers:
            if direct:
                self.total_number_of_customers_go_direct_to_server += 1
                self.proportion_of_customers_go_direct_to_server = round(self.total_number_of_customers_go_direct_to_server/self.total_number_of_customers, 2)
            else:
                self.average_number_of_customers_in_queue = self.average_number_of_customers_in_queue_update()
                self.last_time_number_customer_queue_changed = self.time
                self.number_of_customers_in_queue_at_t -= 1
                self.total_time_spent_in_queue_all_customers_definitive += self.time - customer.arrival_time
                self.total_time_spent_in_queue_all_customers_definitive = round(self.total_time_spent_in_queue_all_customers, 2)
                if customer in self.customers_in_queue_with_t0_counted:
                    self.customers_in_queue_with_t0_counted.remove(customer)

    def server_finish_service_update(self, server):
        self.number_of_busy_servers_at_t -= 1
        server.total_time_of_service_definitive += round(server.time_of_ending_service - server.time_of_begining_service, 2)
        server.total_time_of_service_definitive = round(server.total_time_of_service_definitive, 2)
        for customer in server.customers:
            self.average_number_of_customers_in_system = self.average_number_of_customers_in_system_update()
            self.last_time_number_customer_system_changed = self.time
            self.number_of_customers_in_system_at_t -= 1
            self.total_time_spent_in_system_all_customers_definitive += self.time - customer.arrival_time
            self.total_time_spent_in_system_all_customers_definitive = round(self.total_time_spent_in_system_all_customers, 2)
            server.total_number_of_served_customer += 1

    def customer_renege_update(self, customer):
        # system
        self.average_number_of_customers_in_system = self.average_number_of_customers_in_system_update()
        self.last_time_number_customer_system_changed = self.time
        self.number_of_customers_in_system_at_t -= 1
        self.total_time_spent_in_system_all_customers_definitive += self.time - customer.arrival_time
        self.total_time_spent_in_system_all_customers_definitive = round(self.total_time_spent_in_system_all_customers, 2)
        # queue
        self.average_number_of_customers_in_queue = self.average_number_of_customers_in_queue_update()
        self.last_time_number_customer_queue_changed = self.time
        self.number_of_customers_in_queue_at_t -= 1
        self.total_time_spent_in_queue_all_customers_definitive += self.time - customer.arrival_time
        self.total_time_spent_in_queue_all_customers_definitive = round(self.total_time_spent_in_queue_all_customers, 2)
        if customer in self.customers_in_queue_with_t0_counted:
            self.customers_in_queue_with_t0_counted.remove(customer)

    def customer_delayed_more_than_t0_update(self):
        for customer in self.queue:
            if (self.time - customer.arrival_time) >= self.t0 and customer not in self.customers_in_queue_with_t0_counted:
                self.customers_in_queue_with_t0_counted.append(customer)
                self.number_of_customers_delayed_in_queue_longer_than_t0_time += 1
        self.proportion_of_customers_delayed_in_queue_longer_than_t0_time = round(self.number_of_customers_delayed_in_queue_longer_than_t0_time/\
                                                                                  self.total_number_of_customers, 2)

    def queue_contains_more_than_k0_customers_update(self):
        if self.number_of_customers_in_queue_at_t >= self.k0:
            if self.queue_is_k0 and self.last_time_queue_k0 != self.time:
                self.times_queue_contains_more_than_k0_customers += self.time - self.last_time_queue_k0
                self.times_queue_contains_more_than_k0_customers = round(self.times_queue_contains_more_than_k0_customers, 2)
                self.proportion_of_time_queue_contains_more_than_k0_customers = round(self.times_queue_contains_more_than_k0_customers/self.time, 2)
                self.last_time_queue_k0 = self.time
            elif not self.queue_is_k0:
                self.last_time_queue_k0 = self.time
                self.queue_is_k0 = True
        else:
            if self.queue_is_k0:
                self.times_queue_contains_more_than_k0_customers += self.time - self.last_time_queue_k0
                self.times_queue_contains_more_than_k0_customers = round(self.times_queue_contains_more_than_k0_customers, 2)
                self.proportion_of_time_queue_contains_more_than_k0_customers = round(self.times_queue_contains_more_than_k0_customers/self.time, 2)
                self.last_time_queue_k0 = self.time
            self.queue_is_k0 = False

    def measures_update(self):
        if self.total_number_of_customers == 0 or self.time == 0:
            return
        self.total_time_spent_in_system_all_customers = self.total_time_spent_in_system_all_customers_definitive + sum([self.time - customer.arrival_time
                                                                                                                        for customer in self.queue])
        self.total_time_spent_in_system_all_customers += sum([sum([self.time - customer.arrival_time for customer in server.customers])
                                                              for server in self.servers if server.customers])
        self.total_time_spent_in_system_all_customers = round(self.total_time_spent_in_system_all_customers, 2)
        self.total_time_spent_in_queue_all_customers = self.total_time_spent_in_queue_all_customers_definitive + sum([self.time - customer.arrival_time
                                                                                                                        for customer in self.queue])
        self.total_time_spent_in_queue_all_customers = round(self.total_time_spent_in_queue_all_customers, 2)
        self.customer_delayed_more_than_t0_update()
        self.queue_contains_more_than_k0_customers_update()
        self.arrival_rate = round(self.total_number_of_customers/self.time, 2)
        self.effective_arrival_rate = round((self.total_number_of_customers - self.number_of_customers_turned_away)/self.time, 2)
        for server in self.servers:
            if server.total_time_of_service_definitive:
                if server.customers:
                    server.total_time_of_service = server.total_time_of_service_definitive + round(self.time - server.time_of_begining_service, 2)
                    server.total_time_of_service = round(server.total_time_of_service, 2)
                    server.service_rate = round((server.total_number_of_served_customer+1)/server.total_time_of_service, 2)
                else:
                    server.total_time_of_service = server.total_time_of_service_definitive
                    server.service_rate = round(server.total_number_of_served_customer/server.total_time_of_service, 2)
                server.server_utilization = round(server.total_time_of_service/self.time, 2)
        self.average_service_rate = round(np.mean([server.service_rate for server in self.servers]), 2)
        self.average_server_utilization = round(np.mean([server.server_utilization for server in self.servers]), 2)
        if self.last_time_number_customer_system_changed != self.time:
            self.average_number_of_customers_in_system = self.average_number_of_customers_in_system_update()
            self.last_time_number_customer_system_changed = self.time
        if self.last_time_number_customer_queue_changed != self.time:
            self.average_number_of_customers_in_queue = self.average_number_of_customers_in_queue_update()
            self.last_time_number_customer_queue_changed = self.time
        self.proportion_of_customers_go_direct_to_server = round(self.total_number_of_customers_go_direct_to_server/self.total_number_of_customers, 2)
        self.proportion_of_customers_turned_away = round(self.number_of_customers_turned_away/self.total_number_of_customers, 2)
        try:
            self.average_time_spent_in_system_per_customer = round(self.total_time_spent_in_system_all_customers/(self.total_number_of_customers - \
                                                                                                              self.number_of_customers_turned_away), 2)
        except:
            self.average_time_spent_in_system_per_customer = 0
        try:
            self.average_time_spent_in_queue_per_customer = round(self.total_time_spent_in_queue_all_customers/(self.total_number_of_customers - \
                                                                                                            self.number_of_customers_turned_away - \
                                                                                                           self.total_number_of_customers_go_direct_to_server), 2)
        except:
            self.average_time_spent_in_queue_per_customer = 0

    def next_unit_time(self):
        t = np.floor(self.time)
        for i in range(round(1/self.time_unit_update)+1):
            if round(t+i*self.time_unit_update, 2) > self.time:
                return round(t+i*self.time_unit_update, 2)

    def next_time(self):
        if self.is_paused:
            return self.time
        t = self.next_unit_time()
        if self.events[0] <= t:
            self.time = self.events.pop(0)
        else:
            self.time = t

    def add_event(self, time):
        self.events.append(time)
        self.events.sort()

    def time_sleep(self):
        time.sleep((min(self.events[0], self.time+self.time_unit_update) - self.time)*10**(-self.time_speed))

    def is_arrival_batch(self):
        return bool(np.random.choice(2, p=[1-self.arrival_in_batches_probability, self.arrival_in_batches_probability]))

    def is_priority(self):
        return bool(np.random.choice(2, p=[1-self.priority_probability, self.priority_probability]))

    def is_service_batch(self):
        return bool(np.random.choice(2, p=[1-self.service_to_batch_probability, self.service_to_batch_probability]))

    def is_bulk(self):
        p = self.effect(self.number_of_customers_in_queue_at_t, self.bulk, self.bulk_start, self.bulk_stop, self.bulk_half)
        return bool(np.random.choice(2, p=[p, 1-p]))

    def is_renege(self):
        p = self.effect(self.time, self.renege, self.renege_start, self.renege_stop, self.renege_half)
        return bool(np.random.choice(2, p=[p, 1-p]))

    def is_service_randomly(self):
        return bool(np.random.choice(2, p=[1-self.server_choose_randomly_probability, self.server_choose_randomly_probability]))

    def effect(self, parameter, active, start, stop, half_effect_point):
        if not active or parameter <= start:
            return 1
        return 2/(1+np.e**(np.log(3)*(min(stop, parameter)-start)/(half_effect_point-start)))

    def disturbution(self, d, condition=0):
        if bool(re.fullmatch(r"constant *\( *(\+|-)?\d+(\.\d+)? *\)", d, flags=re.I)):
            c = float(re.search(r"-?\d+\.?\d*", d).group())
            if condition:
                if c >= condition:
                    return round(c, 2)
                raise "Error"
            return round(c, 2)
        elif bool(re.fullmatch(r"disc-uniform *\( *(\+|-)?\d+(\.\d+)? *, *(\+|-)?\d+(\.\d+)? *\)", d, flags=re.I)):
            a, b = map(float, re.findall(r"-?\d+\.?\d*", d))
            assert a < b
            if condition:
                if condition <= a:
                    return round(np.random.randint(a, b+1), 2)
                elif condition <= b:
                    return round(np.random.randint(condition, b+1), 2)
                raise "Error"
            return round(np.random.randint(a, b+1), 2)
        elif bool(re.fullmatch(r"cont-uniform *\( *(\+|-)?\d+(\.\d+)? *, *(\+|-)?\d+(\.\d+)? *\)", d, flags=re.I)):
            a, b = map(float, re.findall(r"-?\d+\.?\d*", d))
            assert a < b
            if condition:
                if condition <= a:
                    return round(np.random.random()*(b-a)+a, 2)
                elif condition <= b:
                    return round(np.random.random()*(b-condition)+condition, 2)
                raise "Error"
            return round(np.random.random()*(b-a)+a, 2)
        elif bool(re.fullmatch(r"normal *\( *(\+|-)?\d+(\.\d+)? *, *(\+|-)?\d+(\.\d+)? *\)", d, flags=re.I)):
            m, s = map(float, re.findall(r"-?\d+\.?\d*", d))
            assert s > 0
            if condition:
                c = norm.sf(condition-0.005, loc=m, scale=s)
                p = 1
                n = condition
                probabilities = []
                while p/c > 0:
                    p = norm.cdf(n+0.005, loc=m, scale=s) - norm.cdf(n-0.005, loc=m, scale=s)
                    probabilities.append(p/c)
                    n = round(n+0.01, 2)
                return np.random.choice(np.arange(condition, n, 0.01), p=probabilities)
            return round(np.random.normal(m, s), 2)
        elif bool(re.fullmatch(r"poisson *\( *(\+|-)?\d+(\.\d+)? *\)", d, flags=re.I)):
            p = float(re.search(r"-?\d+\.?\d*", d).group())
            assert p > 0
            return round(np.random.poisson(p), 2)
        elif bool(re.fullmatch(r"exponential *\( *(\+|-)?\d+(\.\d+)? *\)", d, flags=re.I)):
            l = float(re.search(r"-?\d+\.?\d*", d).group())
            assert l > 0
            return round(np.random.exponential(l), 2)
        elif bool(re.fullmatch(r"gamma *\( *(\+|-)?\d+(\.\d+)? *, *(\+|-)?\d+(\.\d+)? *\)", d, flags=re.I)):
            k, t = map(float, re.findall(r"-?\d+\.?\d*", d))
            assert k > 0 and t > 0
            return round(np.random.gamma(k, t), 2)
        elif bool(re.fullmatch(r"weibull *\( *(\+|-)?\d+(\.\d+)? *\)", d, flags=re.I)):
            a = float(re.search(r"-?\d+\.?\d*", d).group())
            assert a > 0
            return round(np.random.weibull(a), 2)
        elif bool(re.fullmatch(r"lognormal *\( *(\+|-)?\d+(\.\d+)? *, *(\+|-)?\d+(\.\d+)? *\)", d, flags=re.I)):
            m, s = map(float, re.findall(r"-?\d+\.?\d*", d))
            assert s > 0
            return round(np.random.lognormal(m, s), 2)

    def available_server(self):
        return bool(self.number_of_servers - self.number_of_busy_servers_at_t)

    def assign_customer_and_server(self, server, customers, time):
        server.time_of_begining_service = time
        if customers[0].priority:
            server.time_of_ending_service = round(self.time + self.disturbution(self.priority_service_disturbution)*\
                                              self.effect(self.number_of_customers_in_queue_at_t, self.is_service_depend_on_queue_length,
                                                          self.service_dependance_start, self.service_dependance_stop,
                                                          self.length_queue_when_service_time_became_half), 2)
        else:
            server.time_of_ending_service = round(self.time + self.disturbution(self.service_disturbution)*\
                                              self.effect(self.number_of_customers_in_queue_at_t, self.is_service_depend_on_queue_length,
                                                          self.service_dependance_start, self.service_dependance_stop,
                                                          self.length_queue_when_service_time_became_half), 2)
        server.customers = customers
        self.update_servers()
        self.add_event(server.time_of_ending_service)

    def update_servers(self):
        self.servers.sort(key=lambda server: server.time_of_ending_service)

    def customer_arrival(self, arrival_time):
        n = 1
        if self.is_arrival_batch():
            n = round(self.disturbution(self.batch_size_disturbution, condition=1))
        priority = self.is_priority()
        successfully_arrived_customers = 0
        for _ in range(n):
            if self.number_of_customers_in_system_at_t >= self.queue_capacity:
                self.customer_arrival_failure_update()
            else:
                successfully_arrived_customers += 1
        number_of_customers_join_queue = successfully_arrived_customers
        if self.available_server():
            server = self.servers[0]
            if priority:
                customers = [Customer(arrival_time, priority) for _ in range(successfully_arrived_customers)]
                self.assign_customer_and_server(server, customers, arrival_time)
                self.customer_arrival_succeed_update(n=successfully_arrived_customers)
                self.customer_receive_service_update(customers, direct=True)
                return
            m = 1
            if self.is_service_batch():
                m = round(self.disturbution(self.service_batch_size_disturbution, condition=1))
            number_of_customers_recieve_service = min(successfully_arrived_customers, m)
            number_of_customers_join_queue = successfully_arrived_customers - number_of_customers_recieve_service
            customers = [Customer(arrival_time, priority) for _ in range(number_of_customers_recieve_service)]
            self.assign_customer_and_server(server, customers, arrival_time)
            self.customer_arrival_succeed_update(n=number_of_customers_recieve_service)
            self.customer_receive_service_update(customers, direct=True)      
        for _ in range(number_of_customers_join_queue):
            if not priority and self.is_bulk():
                self.customer_arrival_failure_update()
                continue
            customer = Customer(arrival_time, priority)
            if priority or self.discipline == 'FIFO':
                self.queue.append(customer)
            elif self.discipline == 'LIFO':
                self.queue.insert(0, customer)
            elif self.discipline == 'SIRO':
                i = np.random.randint(len(self.queue[i])+1)
                self.queue.insert(i, customer)
            self.customer_arrival_succeed_update()
            self.customer_join_queue_update()

    def reset_server(self, server):
        server.time_of_begining_service = 0
        server.time_of_ending_service = 0
        server.customers = []

    def is_a_server_idle(self):
        for server in self.servers:
            if not server.customers:
                self.update_servers()
                return True
        return False

    def check_finished_servers(self):
        for server in self.servers:
            if self.time != 0 and server.time_of_ending_service == self.time:
                if not self.only_first_and_last:
                    print("server finish service:", self.time)
                self.server_finish_service_update(server)
                self.reset_server(server)
                self.update_servers()
                if not self.only_first_and_last:
                    print(self)
            elif server.time_of_ending_service > self.time:
                break

    def get_arrival(self):
        arrival = self.arrivals.pop(0)
        self.arrivals.append(round(self.arrivals[-1]+self.disturbution(self.arrival_disturbution), 2))
        self.add_event(self.arrivals[-1])
        return arrival

    def service(self):
        n = 1
        if self.is_service_batch():
            n = round(self.disturbution(self.service_batch_size_disturbution, condition=1))
        n = min(n, self.number_of_customers_in_queue_at_t)
        customers = []
        for _ in range(n):
            i = 0
            if not self.queue[0].priority and self.is_service_randomly():
                i = np.random.randint(len(self.queue))
            customers.append(self.queue.pop(i))
        server = self.servers[0]
        self.assign_customer_and_server(server, customers, self.time)
        self.customer_receive_service_update(customers)

    def customer_renege(self):
        indices = []
        for i, customer in enumerate(self.queue):
            if not customer.priority and customer.arrival_time >= self.renege_start and self.is_renege():
                indices.append(i)
        k = 0
        for i in indices:
            self.queue.pop(i-k)
            self.customer_renege_update(customer)
            k += 1

    def run(self):
        print(self)
        print()
        next_arrival_time = self.get_arrival()
        while self.time < self.number_of_unit_of_time_for_simulation:
            if self.time == next_arrival_time:
                if not self.only_first_and_last:
                    print("arrival:", self.time)
                    print()
                self.customer_arrival(self.time)
                next_arrival_time = self.get_arrival()
                if not self.only_first_and_last:
                    print(self)
                    print()
            self.check_finished_servers()
            while self.is_a_server_idle() and self.queue:
                if not self.only_first_and_last:
                    print("service:", self.time)
                    print()
                self.service()
                if not self.only_first_and_last:
                    print(self)
                    print()
            self.measures_update()
            self.customer_renege()
            self.next_time()
            self.time_sleep()
        print("simulation is finnished:\n", self)
