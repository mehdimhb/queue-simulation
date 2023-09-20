import streamlit as st
from src.simulation import Simulation
from src.event import EventHeap
from src.math_utils import make_str


# set title of the page
st.set_page_config(
    page_title="Queue Simulation",
)

# title
st.title("Queue Simulation")


# settings
st.header("Settings")

# general settings
st.subheader("General Settings")

col1, col2, col3, col4 = st.columns(4)

queue_capacity = col1.number_input("Queue Capacity", 0, step=1)
no_of_servers = col2.number_input("Number of Servers", 0, step=1)
speed = col3.slider("Simulation Speed", 0, 3, step=1)
if speed == 3:
    speed = None
duration = col4.slider("Simulation Duration", 100, 10000, step=100)

# arrival settings
st.subheader("Arrival Settings")

col1, col2, col3 = st.columns([2, 1, 1])

arrival_distribution = col1.selectbox(
    "Interarrival Time Distribution",
    ["Constant", "Continuous Uniform", "Normal", "Exponential"],
    key=101
)
match arrival_distribution:
    case "Constant":
        arr_dis_param1 = col2.number_input("c", 0.01, step=0.01, key=1)
        arr_dis_param2 = None
    case "Continuous Uniform":
        arr_dis_param1 = col2.number_input("a", 0.01, step=0.01, key=2)
        arr_dis_param2 = col3.number_input("b", arr_dis_param1+0.01, step=0.01, key=3)
    case "Normal":
        arr_dis_param1 = col2.number_input("mean", step=0.01, key=4)
        arr_dis_param2 = col3.number_input("sd", 0.01, step=0.01, key=5)
    case "Exponential":
        arr_dis_param1 = col2.number_input("\u03BB", 0.01, step=0.01, key=6)
        arr_dis_param2 = None
arrival_distribution = make_str(arrival_distribution, arr_dis_param1, arr_dis_param2)

arrival_batch = st.checkbox("Arrival could be in batch")
if arrival_batch:
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
    arrival_batch_probability = col1.number_input(
        "Probability",
        0.00, 1.00,
        step=0.01,
        help="Probability of an arrival be in batch")
    arrival_batch_distribution = col2.selectbox(
        "Batch Size Distribution",
        ["Constant", "Discrete Uniform", "Normal", "Poisson"],
        key=102
    )
    match arrival_batch_distribution:
        case "Constant":
            arr_batch_dis_param1 = col3.number_input("c", 1, step=1, key=7)
            arr_batch_dis_param2 = None
        case "Discrete Uniform":
            arr_batch_dis_param1 = col3.number_input("a", 1, step=1, key=8)
            arr_batch_dis_param2 = col4.number_input("b", arr_batch_dis_param1+1, step=1, key=9)
        case "Normal":
            arr_batch_dis_param1 = col3.number_input("mean", step=0.01, key=10)
            arr_batch_dis_param2 = col4.number_input("sd", 0.01, step=0.01, key=11)
        case "Poisson":
            arr_batch_dis_param1 = col3.number_input("p", 0.01, step=0.01, key=12)
            arr_batch_dis_param2 = None
    arrival_batch_distribution = make_str(arrival_batch_distribution, arr_batch_dis_param1, arr_batch_dis_param2)
else:
    arrival_batch_probability, arrival_batch_distribution = 0, None

# service settings
st.subheader("Service Settings")

col1, col2, col3 = st.columns([2, 1, 1])

service_distribution = col1.selectbox(
    "Service Time Distribution",
    ["Constant", "Continuous Uniform", "Normal", "Exponential"],
    key=103
)
match service_distribution:
    case "Constant":
        ser_dis_param1 = col2.number_input("c", 0.01, step=0.01, key=13)
        ser_dis_param2 = None
    case "Continuous Uniform":
        ser_dis_param1 = col2.number_input("a", 0.01, step=0.01, key=14)
        ser_dis_param2 = col3.number_input("b", ser_dis_param1+0.01, step=0.01, key=15)
    case "Normal":
        ser_dis_param1 = col2.number_input("mean", step=0.01, key=16)
        ser_dis_param2 = col3.number_input("sd", 0.01, step=0.01, key=17)
    case "Exponential":
        ser_dis_param1 = col2.number_input("\u03BB", 0.01, step=0.01, key=18)
        ser_dis_param2 = None
service_distribution = make_str(service_distribution, ser_dis_param1, ser_dis_param2)

service_batch = st.checkbox("Server could service to batch")
if service_batch:
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
    service_batch_probability = col1.number_input(
        "Probability",
        0.00, 1.00,
        step=0.01,
        help="Probability of a server select a batch of customers instead \
            of one customer")
    service_batch_distribution = col2.selectbox(
        "Batch Size Distribution",
        ["Constant", "Discrete Uniform", "Normal", "Poisson"],
        key=104
    )
    match service_batch_distribution:
        case "Constant":
            ser_batch_dis_param1 = col3.number_input("c", 1, step=1, key=19)
            ser_batch_dis_param2 = None
        case "Discrete Uniform":
            ser_batch_dis_param1 = col3.number_input("a", 1, step=1, key=20)
            ser_batch_dis_param2 = col4.number_input("b", ser_batch_dis_param1+1, step=1, key=21)
        case "Normal":
            ser_batch_dis_param1 = col3.number_input("mean", step=0.01, key=22)
            ser_batch_dis_param2 = col4.number_input("sd", 0.01, step=0.01, key=23)
        case "Poisson":
            ser_batch_dis_param1 = col3.number_input("p", 0.01, step=0.01, key=24)
            ser_batch_dis_param2 = None
    service_batch_distribution = make_str(service_batch_distribution, ser_batch_dis_param1, ser_batch_dis_param2)
else:
    service_batch_probability, service_batch_distribution = 0, None

server_select_rand = st.checkbox("Server could select customers randomly instead \
    of always selecting the head of the queue")
if server_select_rand:
    col, _ = st.columns(2)
    server_select_rand_probability = col.number_input(
        "Probability",
        0.00, 1.00,
        step=0.01,
        help="Probability of a server select customers randomly instead of \
            selecting the head of the queue"
    )
else:
    server_select_rand_probability = 0

service_dependency = st.checkbox("Service time should depend on the length \
    of the queue")
if service_dependency:
    col1, col2, col3 = st.columns(3)
    service_dependency_start = col1.number_input(
        "Start",
        1,
        step=1,
        help="The length of the queue in which dependency starts to take place"
    )
    service_dependency_half = col2.number_input(
        "Half",
        1,
        step=1,
        help="The length of the queue in which service time would be half of the usual"
    )
    service_dependency_stop = col3.number_input(
        "Stop",
        1,
        step=1,
        help="The length of the queue in which further increasing will have \
            no effect on service time"
    )
else:
    service_dependency_start, service_dependency_half, service_dependency_stop = None, None, None

priority_customer = st.checkbox("Some Customers would have priority in \
    receiving service")
if priority_customer:
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
    priority_probability = col1.number_input(
        "Probability",
        0.00, 1.00,
        step=0.01,
        help="Probability of a customer to have priority")
    priority_service_distribution = col2.selectbox(
        "Service Time Dist. of Priority Customers",
        ["Constant", "Continuous Uniform", "Normal", "Poisson"],
        key=105
    )
    match priority_service_distribution:
        case "Constant":
            ser_tp_dis_param1 = col3.number_input("c", 0.01, step=0.01, key=25)
            ser_tp_dis_param2 = None
        case "Continuous Uniform":
            ser_tp_dis_param1 = col3.number_input("a", 0.01, step=0.01, key=26)
            ser_tp_dis_param2 = col4.number_input("b", ser_tp_dis_param1+0.01, step=0.01, key=27)
        case "Normal":
            ser_tp_dis_param1 = col3.number_input("mean", step=0.01, key=28)
            ser_tp_dis_param2 = col4.number_input("sd", 0.01, step=0.01, key=29)
        case "Exponential":
            ser_tp_dis_param1 = col3.number_input("\u03BB", 0.01, step=0.01, key=30)
            ser_tp_dis_param2 = None
    priority_service_distribution = make_str(priority_service_distribution, ser_tp_dis_param1, ser_tp_dis_param2)
else:
    priority_probability, priority_service_distribution = 0, None

# queue behavior and stats settings
st.subheader("Queue Behavior and Stats Settings")

bulk = st.checkbox("Bulk (Customers could decide not to join the queue when \
    the length of the queue is too long)")
if bulk:
    col1, col2, col3 = st.columns(3)
    bulk_start = col1.number_input(
        "Start",
        1,
        step=1,
        help="The length of the queue in which probability of bulking begin \
            to increase from 0.0"
    )
    bulk_half = col2.number_input(
        "Half",
        1,
        step=1,
        help="The length of the queue in which probability of bulking is 0.5"
    )
    bulk_stop = col3.number_input(
        "Stop",
        1,
        step=1,
        help="The length of the queue in which further increasing will have \
            no effect on probability of bulking"
    )
else:
    bulk_start, bulk_half, bulk_stop = None, None, None

renege = st.checkbox("Renege (Customers could leave the queue if they've \
    been waiting for too long in the queue)")
if renege:
    col1, col2, col3 = st.columns(3)
    renege_start = col1.number_input(
        "Start",
        1,
        step=1,
        help="The time spent in the queue in which probability of reneging \
            begin to increase from 0.0"
    )
    renege_half = col2.number_input(
        "Half",
        1,
        step=1,
        help="The length of the queue in which probability of reneging is 0.5"
    )
    renege_stop = col3.number_input(
        "Stop",
        1,
        step=1,
        help="The time spent in the queue in which further increasing will\
            have no effect on probability of reneging"
    )
else:
    renege_start, renege_half, renege_stop = None, None, None

col1, col2, col3 = st.columns([2, 1, 1])
discipline = col1.selectbox(
        "Queue behavior discipline",
        ["FIFO (First in first out)",
         "LIFO (Last in first out)",
         "SIRO (Service in random order)"]
)[:4]
t_star = col2.number_input(
    "t*",
    1,
    step=1,
    help="Used in Statistics: proportion of customers delayed in the queue \
        more than t* time"
)
k_star = col3.number_input(
    "k*",
    1,
    step=1,
    help="Used in Statistics: proportion of time in which the queue contained \
        more than k* customers"
)
# simulation
st.header("Simulation")

st.write("")
if st.button("Start Simulation", type="primary"):
    with st.spinner(text="simulating..."):
        event_heap = EventHeap()
        simulation = Simulation(
            event_heap,
            queue_capacity,
            no_of_servers,
            arrival_distribution,
            service_distribution,
            discipline,
            t_star,
            k_star,
            speed,
            duration,
            arrival_batch_probability,
            arrival_batch_distribution,
            service_batch_probability,
            service_batch_distribution,
            service_dependency,
            service_dependency_start,
            service_dependency_half,
            service_dependency_stop,
            server_select_rand_probability,
            priority_probability,
            priority_service_distribution,
            bulk,
            bulk_start,
            bulk_half,
            bulk_stop,
            renege,
            renege_start,
            renege_half,
            renege_stop
        )

        simulation.run()

        st.markdown(f"""
                    |Statistics|Result|
                    |:-|:-:|
                    |All Time Customers|{simulation.system.all_time_no_of_customers}|
                    |All Time Customers in System|{simulation.system.all_time_no_of_customers_system}|
                    |Average Customers in System|{simulation.system.average_no_of_customers_system}|
                    |Average Time Spent per Customers in System|{simulation.system.average_time_spent_per_customer}|
                    |All Time Customers in Queue|{simulation.system.all_time_no_of_customers_queue}|
                    |Average Customers in Queue|{simulation.system.queue.average_no_of_customers}|
                    |Average Time Spent per Customers in Queue|{simulation.system.queue.average_time_spent_per_customer}|
                    |All Time Customers in Service Center|{simulation.system.all_time_no_of_customers_service_center}|
                    |Average Customers in Service Center|{simulation.system.service_center.average_no_of_customers}|
                    |Average Time Spent per Customers in Service Center|{simulation.system.service_center.average_time_spent_per_customer}|
                    |Departed Customers|{simulation.system.no_of_finished_customers} ({round(100*simulation.system.no_of_finished_customers/simulation.system.all_time_no_of_customers, 2) if simulation.system.all_time_no_of_customers else 0.0}%)|
                    |Still Waiting Customers|{simulation.system.no_of_unfinished_customers} ({round(100*simulation.system.no_of_unfinished_customers/simulation.system.all_time_no_of_customers, 2) if simulation.system.all_time_no_of_customers else 0.0}%)|
                    |Still Waiting Customers in Queue|{len(simulation.system.queue)} ({round(100*len(simulation.system.queue)/simulation.system.no_of_unfinished_customers, 2) if simulation.system.no_of_unfinished_customers else 0.0}%)|
                    |Still Waiting Customers in Service Center|{len(simulation.system.service_center)} ({round(100*len(simulation.system.service_center)/simulation.system.no_of_unfinished_customers, 2) if simulation.system.no_of_unfinished_customers else 0.0}%)|
                    |Turned Away Customers Due to Maximum Capacity|{simulation.system.no_of_customers_turned_away} ({round(100*simulation.system.proportion_of_customers_turned_away, 2)}%)|
                    |Bulked Customers|{simulation.system.no_of_bulking} ({round(100*simulation.system.proportion_of_bulking, 2)}%)|
                    |Reneged Customers|{simulation.system.queue.no_of_reneging} ({round(100*simulation.system.queue.proportion_of_reneging, 2)}%)|
                    |Customers Skip Queue to Service Center|{simulation.system.no_of_customers_skip_queue} ({round(100*simulation.system.proportion_of_customers_skip_queue, 2)}%)|
                    |Customers Delayed Longer than {simulation.system.queue.t_star}s|{simulation.system.queue.no_of_customers_delayed_longer_t_star} ({round(100*simulation.system.queue.proportion_of_customers_delayed_longer_t_star, 2)}%)|
                    |Percent of Time Queue Contained More than {simulation.system.queue.k_star}|{simulation.system.queue.total_time_queue_contains_more_k_star_customers} ({round(100*simulation.system.queue.proportion_of_time_queue_contains_more_k_star_customers, 2)}%)|
                    |Arrivals|{simulation.system.no_of_arrivals}|
                    |Arrival Rate|{simulation.system.arrival_rate}|
                    |Service Rate|{simulation.system.service_center.service_rate}|
                    |Average Service Rate|{simulation.system.service_center.average_service_rate}|
                    |Average Server Utilization|{simulation.system.service_center.average_server_utilization}|
                    |Average Arrival Batch Size|{simulation.system.average_arrival_batch_size}|
                    |Average Service Batch Size|{simulation.system.service_center.average_service_batch_size}|
        """)
