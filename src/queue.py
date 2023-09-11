import numpy as np
#from service_center import Server
#from src.simulation import Customer


class Queue:
    def __init__(
        self,
        queue_capacity=np.inf,
        no_of_servers=2,
        arrival_distribution='exponential(0.5)',
        arrival_batch_probability=0,
        arrival_batch_distribution='uniform(2, 4)',
        service_distribution='normal(1, 1)',
        service_batch_probability=0,
        service_batch_distribution='uniform(2, 4)',
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
        speed=0,
        duration=100
    ):
        # system properties
        self.queue_capacity = queue_capacity
        self.no_of_servers = no_of_servers

        # arrival properties
        self.arrival_distribution = arrival_distribution
        self.arrival_batch_probability = arrival_batch_probability
        self.arrival_batch_distribution = arrival_batch_distribution
        self.priority_probability = priority_probability
        self.priority_service_distribution = priority_service_distribution

        # service properties
        self.service_distribution = service_distribution
        self.service_batch_probability = service_batch_probability
        self.service_batch_distribution = service_batch_distribution
        self.server_select_rand_probability = server_select_rand_probability
        self.service_dependency = service_dependency
        self.service_dependency_start = service_dependency_start
        self.service_dependency_stop = service_dependency_stop
        self.service_dependency_half = service_dependency_half

        # queue behavior and discipline
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
        self.speed = speed
        self.TIME_UPDATE_UNIT = 0.1
        self.duration = duration
        self.is_paused = False

        self.arrival_rate = 0
        self.effective_arrival_rate = 0
        self.average_service_rate = 0

        self.total_no_of_customers = 0
        self.total_no_of_customers_go_directly_to_server = 0
        self.proportion_of_customers_go_directly_to_server = 0
        self.no_of_customers_in_system_right_now = 0
        self.number_of_customers_in_queue_at_t = 0
        self.last_time_no_of_customers_system_changed = 0
        self.last_time_no_of_customers_queue_changed = 0
        self.average_no_of_customers_in_system = 0
        self.average_no_of_customers_in_queue = 0
        self.total_time_spent_in_system_all_customers = 0
        self.total_time_spent_in_queue_all_customers = 0
        self.total_time_spent_in_system_all_customers_definitive = 0
        self.total_time_spent_in_queue_all_customers_definitive = 0
        self.average_time_spent_in_system_per_customer = 0
        self.average_time_spent_in_queue_per_customer = 0
        self.no_of_busy_servers_right_now = 0
        self.average_server_utilization = 0

        self.t_star = t_star
        self.customers_in_queue_with_t_star_delayed = []
        self.no_of_customers_delayed_in_queue_longer_than_t_star_time = 0
        self.proportion_of_customers_delayed_in_queue_longer_than_t_star_time = 0
        self.k0 = k_star
        self.total_time_queue_contains_more_than_k_star_customers = 0
        self.last_time_queue_contained_k_star = 0
        self.queue_is_containing_k_star = False
        self.proportion_of_time_queue_contains_more_than_k_star_customers = 0
        self.number_of_customers_turned_away = 0
        self.proportion_of_customers_turned_away = 0

        # storage information
        self.queue = []
        self.servers = [Server(i) for i in range(self.no_of_servers)]

    def __str__(self):
        qq = [str(x) for x in self.queue]
        s = [str(x) for x in self.servers]
        ss = [(x.id, x.service_rate) for x in self.servers]
        sss = [(x.id, x.server_utilization) for x in self.servers]
        s3 = [(x.id, x.total_time_of_service_definitive) for x in self.servers]
        s4 = [(x.id, x.total_time_of_service) for x in self.servers]
        s5 = [(x.id, x.total_number_of_served_customer) for x in self.servers]
        return f"""total_number_of_customers = {self.total_no_of_customers}
        arrival_rate = {self.arrival_rate}
        effective_arrival_rate = {self.effective_arrival_rate}
        number_of_busy_servers_at_t = {self.no_of_busy_servers_right_now}
        total_time_of_services_definitive = {s3}
        total_time_of_services = {s4}
        total_number_of_served_customer = {s5}
        service_rate = {ss}
        average_service_rate = {self.average_service_rate}
        server_utilization = {sss}
        average_server_utilization = {self.average_server_utilization}
        total_number_of_customers_go_direct_to_server = {self.total_no_of_customers_go_directly_to_server}
        proportion_of_customers_go_direct_to_server = {self.proportion_of_customers_go_directly_to_server}
        number_of_customers_in_system_at_t = {self.no_of_customers_in_system_right_now}
        number_of_customers_in_queue_at_t = {self.number_of_customers_in_queue_at_t}
        average_number_of_customers_in_system = {self.average_no_of_customers_in_system}
        average_number_of_customers_in_queue = {self.average_no_of_customers_in_queue}
        total_time_spent_in_system_per_customer = {self.total_time_spent_in_system_all_customers}
        total_time_spent_in_queue_per_customer = {self.total_time_spent_in_queue_all_customers}
        total_time_spent_in_system_all_customers_definitive = {self.total_time_spent_in_system_all_customers_definitive}
        total_time_spent_in_queue_all_customers_definitive = {self.total_time_spent_in_queue_all_customers_definitive}
        average_time_spent_in_system_per_customer = {self.average_time_spent_in_system_per_customer}
        average_time_spent_in_queue_per_customer = {self.average_time_spent_in_queue_per_customer}
        number_of_customers_delayed_in_queue_longer_than_{self.t_star}_time = {self.no_of_customers_delayed_in_queue_longer_than_t_star_time}
        proportion_of_customers_delayed_in_queue_longer_than_{self.t_star}_time = {self.proportion_of_customers_delayed_in_queue_longer_than_t_star_time}
        times_queue_contains_more_than_{self.k0}_customers = {self.total_time_queue_contains_more_than_k_star_customers}
        proportion_of_time_queue_contains_more_than_{self.k0}_customers = {self.proportion_of_time_queue_contains_more_than_k_star_customers}
        number_of_customers_turned_away = {self.number_of_customers_turned_away}
        proportion_of_customers_turned_away = {self.proportion_of_customers_turned_away}
        queue = {qq}
        servers = {s}"""

    def average_number_of_customers_in_system_update(self):
        if not self.time:
            return 0
        return round(self.average_no_of_customers_in_system*(self.last_time_no_of_customers_system_changed/self.time)+\
            (self.time - self.last_time_no_of_customers_system_changed)*self.no_of_customers_in_system_right_now/self.time, 2)

    def average_number_of_customers_in_queue_update(self):
        if not self.time:
            return 0
        return round(self.average_no_of_customers_in_queue*(self.last_time_no_of_customers_queue_changed/self.time)+\
            (self.time - self.last_time_no_of_customers_queue_changed)*self.number_of_customers_in_queue_at_t/self.time, 2)

    def customer_arrival_failure_update(self):
        self.number_of_customers_turned_away += 1
        self.total_no_of_customers += 1
        self.proportion_of_customers_turned_away = round(self.number_of_customers_turned_away/self.total_no_of_customers, 2)

    def customer_arrival_succeed_update(self, n=1):
        self.total_no_of_customers += n
        self.average_no_of_customers_in_system = self.average_number_of_customers_in_system_update()
        self.last_time_no_of_customers_system_changed = self.time
        self.no_of_customers_in_system_right_now += n

    def customer_join_queue_update(self):
        self.average_no_of_customers_in_queue = self.average_number_of_customers_in_queue_update()
        self.last_time_no_of_customers_queue_changed = self.time
        self.number_of_customers_in_queue_at_t += 1

    def customer_receive_service_update(self, customers, direct=False):
        self.no_of_busy_servers_right_now += 1
        for customer in customers:
            if direct:
                self.total_no_of_customers_go_directly_to_server += 1
                self.proportion_of_customers_go_directly_to_server = round(self.total_no_of_customers_go_directly_to_server/self.total_no_of_customers, 2)
            else:
                self.average_no_of_customers_in_queue = self.average_number_of_customers_in_queue_update()
                self.last_time_no_of_customers_queue_changed = self.time
                self.number_of_customers_in_queue_at_t -= 1
                self.total_time_spent_in_queue_all_customers_definitive += self.time - customer.arrival_time
                self.total_time_spent_in_queue_all_customers_definitive = round(self.total_time_spent_in_queue_all_customers, 2)
                if customer in self.customers_in_queue_with_t_star_delayed:
                    self.customers_in_queue_with_t_star_delayed.remove(customer)

    def server_finish_service_update(self, server):
        self.no_of_busy_servers_right_now -= 1
        server.total_time_of_service_definitive += round(server.time_of_ending_service - server.time_of_begining_service, 2)
        server.total_time_of_service_definitive = round(server.total_time_of_service_definitive, 2)
        for customer in server.customers:
            self.average_no_of_customers_in_system = self.average_number_of_customers_in_system_update()
            self.last_time_no_of_customers_system_changed = self.time
            self.no_of_customers_in_system_right_now -= 1
            self.total_time_spent_in_system_all_customers_definitive += self.time - customer.arrival_time
            self.total_time_spent_in_system_all_customers_definitive = round(self.total_time_spent_in_system_all_customers, 2)
            server.total_number_of_served_customer += 1

    def customer_renege_update(self, customer):
        # system
        self.average_no_of_customers_in_system = self.average_number_of_customers_in_system_update()
        self.last_time_no_of_customers_system_changed = self.time
        self.no_of_customers_in_system_right_now -= 1
        self.total_time_spent_in_system_all_customers_definitive += self.time - customer.arrival_time
        self.total_time_spent_in_system_all_customers_definitive = round(self.total_time_spent_in_system_all_customers, 2)
        # queue
        self.average_no_of_customers_in_queue = self.average_number_of_customers_in_queue_update()
        self.last_time_no_of_customers_queue_changed = self.time
        self.number_of_customers_in_queue_at_t -= 1
        self.total_time_spent_in_queue_all_customers_definitive += self.time - customer.arrival_time
        self.total_time_spent_in_queue_all_customers_definitive = round(self.total_time_spent_in_queue_all_customers, 2)
        if customer in self.customers_in_queue_with_t_star_delayed:
            self.customers_in_queue_with_t_star_delayed.remove(customer)

    def customer_delayed_more_than_t0_update(self):
        for customer in self.queue:
            if (self.time - customer.arrival_time) >= self.t_star and customer not in self.customers_in_queue_with_t_star_delayed:
                self.customers_in_queue_with_t_star_delayed.append(customer)
                self.no_of_customers_delayed_in_queue_longer_than_t_star_time += 1
        self.proportion_of_customers_delayed_in_queue_longer_than_t_star_time = round(self.no_of_customers_delayed_in_queue_longer_than_t_star_time/\
                                                                                  self.total_no_of_customers, 2)

    def queue_contains_more_than_k0_customers_update(self):
        if self.number_of_customers_in_queue_at_t >= self.k0:
            if self.queue_is_containing_k_star and self.last_time_queue_contained_k_star != self.time:
                self.total_time_queue_contains_more_than_k_star_customers += self.time - self.last_time_queue_contained_k_star
                self.total_time_queue_contains_more_than_k_star_customers = round(self.total_time_queue_contains_more_than_k_star_customers, 2)
                self.proportion_of_time_queue_contains_more_than_k_star_customers = round(self.total_time_queue_contains_more_than_k_star_customers/self.time, 2)
                self.last_time_queue_contained_k_star = self.time
            elif not self.queue_is_containing_k_star:
                self.last_time_queue_contained_k_star = self.time
                self.queue_is_containing_k_star = True
        else:
            if self.queue_is_containing_k_star:
                self.total_time_queue_contains_more_than_k_star_customers += self.time - self.last_time_queue_contained_k_star
                self.total_time_queue_contains_more_than_k_star_customers = round(self.total_time_queue_contains_more_than_k_star_customers, 2)
                self.proportion_of_time_queue_contains_more_than_k_star_customers = round(self.total_time_queue_contains_more_than_k_star_customers/self.time, 2)
                self.last_time_queue_contained_k_star = self.time
            self.queue_is_containing_k_star = False

    def measures_update(self):
        if self.total_no_of_customers == 0 or self.time == 0:
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
        self.arrival_rate = round(self.total_no_of_customers/self.time, 2)
        self.effective_arrival_rate = round((self.total_no_of_customers - self.number_of_customers_turned_away)/self.time, 2)
        for server in self.servers:
            if server.total_time_of_service_definitive:
                if server.customers:
                    server.total_time_of_service = server.total_time_of_service_definitive + round(self.time - server.time_of_beginning_service, 2)
                    server.total_time_of_service = round(server.total_time_of_service, 2)
                    server.service_rate = round((server.total_number_of_served_customer+1)/server.total_time_of_service, 2)
                else:
                    server.total_time_of_service = server.total_time_of_service_definitive
                    server.service_rate = round(server.total_number_of_served_customer/server.total_time_of_service, 2)
                server.server_utilization = round(server.total_time_of_service/self.time, 2)
        self.average_service_rate = round(np.mean([server.service_rate for server in self.servers]), 2)
        self.average_server_utilization = round(np.mean([server.server_utilization for server in self.servers]), 2)
        if self.last_time_no_of_customers_system_changed != self.time:
            self.average_no_of_customers_in_system = self.average_number_of_customers_in_system_update()
            self.last_time_no_of_customers_system_changed = self.time
        if self.last_time_no_of_customers_queue_changed != self.time:
            self.average_no_of_customers_in_queue = self.average_number_of_customers_in_queue_update()
            self.last_time_no_of_customers_queue_changed = self.time
        self.proportion_of_customers_go_directly_to_server = round(self.total_no_of_customers_go_directly_to_server/self.total_no_of_customers, 2)
        self.proportion_of_customers_turned_away = round(self.number_of_customers_turned_away/self.total_no_of_customers, 2)
        try:
            self.average_time_spent_in_system_per_customer = round(self.total_time_spent_in_system_all_customers/(self.total_no_of_customers - \
                                                                                                              self.number_of_customers_turned_away), 2)
        except:
            self.average_time_spent_in_system_per_customer = 0
        try:
            self.average_time_spent_in_queue_per_customer = round(self.total_time_spent_in_queue_all_customers/(self.total_no_of_customers - \
                                                                                                            self.number_of_customers_turned_away - \
                                                                                                           self.total_no_of_customers_go_directly_to_server), 2)
        except:
            self.average_time_spent_in_queue_per_customer = 0

    def is_arrival_batch(self):
        return bool(np.random.choice(2, p=[1-self.arrival_batch_probability, self.arrival_batch_probability]))

    def is_priority(self):
        return bool(np.random.choice(2, p=[1-self.priority_probability, self.priority_probability]))

    def is_service_batch(self):
        return bool(np.random.choice(2, p=[1-self.service_batch_probability, self.service_batch_probability]))

    def is_bulk(self):
        p = self.effect(self.number_of_customers_in_queue_at_t, self.bulk, self.bulk_start, self.bulk_stop, self.bulk_half)
        return bool(np.random.choice(2, p=[p, 1-p]))

    def is_renege(self):
        p = self.effect(self.time, self.renege, self.renege_start, self.renege_stop, self.renege_half)
        return bool(np.random.choice(2, p=[p, 1-p]))

    def is_service_randomly(self):
        return bool(np.random.choice(2, p=[1-self.server_select_rand_probability, self.server_select_rand_probability]))

    def effect(self, parameter, active, start, stop, half_effect_point):
        if not active or parameter <= start:
            return 1
        return 2/(1+np.e**(np.log(3)*(min(stop, parameter)-start)/(half_effect_point-start)))

    def available_server(self):
        return bool(self.no_of_servers - self.no_of_busy_servers_right_now)

    def assign_customer_and_server(self, server, customers, time):
        server.time_of_begining_service = time
        if customers[0].priority:
            server.time_of_ending_service = round(self.time + self.distribution(self.priority_service_distribution)*\
                                              self.effect(self.number_of_customers_in_queue_at_t, self.service_dependency,
                                                          self.service_dependency_start, self.service_dependency_stop,
                                                          self.service_dependency_half), 2)
        else:
            server.time_of_ending_service = round(self.time + self.distribution(self.service_distribution)*\
                                              self.effect(self.number_of_customers_in_queue_at_t, self.service_dependency,
                                                          self.service_dependency_start, self.service_dependency_stop,
                                                          self.service_dependency_half), 2)
        server.customers = customers
        self.update_servers()
        self.add_event(server.time_of_ending_service)

    def update_servers(self):
        self.servers.sort(key=lambda server: server.time_of_ending_service)

    def customer_arrival(self, arrival_time):
        n = 1
        if self.is_arrival_batch():
            n = round(self.distribution(self.arrival_batch_distribution, condition=1))
        priority = self.is_priority()
        successfully_arrived_customers = 0
        for _ in range(n):
            if self.no_of_customers_in_system_right_now >= self.queue_capacity:
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
                m = round(self.distribution(self.service_batch_distribution, condition=1))
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

    def service(self):
        n = 1
        if self.is_service_batch():
            n = round(self.distribution(self.service_batch_distribution, condition=1))
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
        while self.time < self.duration:
            event = self.get_next_event()
            while self.time < self.duration and self.time < self.event.time:
                self.measures_update()
                self.customer_renege()
                self.next_time()
                self.time_sleep()
            if event.type == "Arrival":
                self.customer_arrival(self.time)
                self.add_new_arrival()
            elif event.type == "Service End":
                self.check_finished_servers()
                self.service()
            self.measures_update()
            self.customer_renege()
            self.next_time()
            self.time_sleep()
