import streamlit as st

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

col1, col2, col3 = st.columns(3)

system_capacity = col1.number_input("System Capacity", 0, step=1)
no_of_servers = col2.number_input("Number of Servers", 0, step=1)
speed = col3.slider("Simulation Speed", 0, 3, step=1)

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
        arr_dis_param2 = col3.number_input("sd", step=0.01, key=5)
    case "Exponential":
        arr_dis_param1 = col2.number_input("\u03BB", 0.01, step=0.01, key=6)
        arr_dis_param2 = None

arrival_batches = st.checkbox("Arrival could be in batch")
if arrival_batches:
    col1, col2, col3 = st.columns([2, 1, 1])
    arrival_batch_distribution = col1.selectbox(
        "Batch Size Distribution",
        ["Constant", "Discrete Uniform", "Normal", "Poisson"],
        key=102
    )
    match arrival_batch_distribution:
        case "Constant":
            arr_batch_dis_param1 = col2.number_input("c", 1, step=1, key=7)
            arr_batch_dis_param2 = None
        case "Discrete Uniform":
            arr_batch_dis_param1 = col2.number_input("a", 1, step=1, key=8)
            arr_batch_dis_param2 = col3.number_input("b", arr_batch_dis_param1+1, step=1, key=9)
        case "Normal":
            arr_batch_dis_param1 = col2.number_input("mean", step=0.01, key=10)
            arr_batch_dis_param2 = col3.number_input("sd", step=0.01, key=11)
        case "Poisson":
            arr_batch_dis_param1 = col2.number_input("p", 0.01, step=0.01, key=12)
            arr_batch_dis_param2 = None

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
        ser_dis_param2 = col3.number_input("sd", step=0.01, key=17)
    case "Exponential":
        ser_dis_param1 = col2.number_input("\u03BB", 0.01, step=0.01, key=18)
        ser_dis_param2 = None

service_batches = st.checkbox("Server could service to batch")
if service_batches:
    col1, col2, col3 = st.columns([2, 1, 1])
    service_batch_distribution = col1.selectbox(
        "Batch Size Distribution",
        ["Constant", "Discrete Uniform", "Normal", "Poisson"],
        key=104
    )
    match service_batch_distribution:
        case "Constant":
            ser_batch_dis_param1 = col2.number_input("c", 1, step=1, key=19)
            ser_batch_dis_param2 = None
        case "Discrete Uniform":
            ser_batch_dis_param1 = col2.number_input("a", 1, step=1, key=20)
            ser_batch_dis_param2 = col3.number_input("b", ser_batch_dis_param1+1, step=1, key=21)
        case "Normal":
            ser_batch_dis_param1 = col2.number_input("mean", step=0.01, key=22)
            ser_batch_dis_param2 = col3.number_input("sd", step=0.01, key=23)
        case "Poisson":
            ser_batch_dis_param1 = col2.number_input("p", 0.01, step=0.01, key=24)
            ser_batch_dis_param2 = None

select_randomly = st.checkbox("Server could select customers randomly instead \
    of always selecting the head of the queue")
if select_randomly:
    col, _ = st.columns(2)
    select_randomly_probability = col.number_input(
        "Probability",
        0.00, 1.00,
        step=0.01,
        help="Probability of a server select customers randomly instead of \
            selecting the head of the queue"
    )

ser_dependency = st.checkbox("Service time should depend on the length \
    of the queue")
if ser_dependency:
    col1, col2, col3 = st.columns(3)
    ser_dep_start = col1.text_input(
        "Start",
        help="The length of the queue in which dependency starts to take place"
    )
    ser_dep_stop = col2.text_input(
        "Stop",
        help="The length of the queue in which further increasing will have \
            no effect on service time"
    )
    ser_dep_half = col3.text_input(
        "Half",
        help="The length of the queue in which service time would be half of the usual"
    )

priority_customer = st.checkbox("Some Customers would have priority in \
    receiving service")
if priority_customer:
    col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
    priority_probability = col1.number_input(
        "Probability",
        0.00, 1.00,
        step=0.01,
        help="Probability of a customer to have priority")
    service_time_priority_distribution = col2.selectbox(
        "Service Time Dist. of Priority Customers",
        ["Constant", "Continuous Uniform", "Normal", "Poisson"],
        key=105
    )
    match service_time_priority_distribution:
        case "Constant":
            ser_tp_dis_param1 = col3.number_input("c", 0.01, step=0.01, key=25)
            ser_tp_dis_param2 = None
        case "Continuous Uniform":
            ser_tp_dis_param1 = col3.number_input("a", 0.01, step=0.01, key=26)
            ser_tp_dis_param2 = col4.number_input("b", ser_tp_dis_param1+0.01, step=0.01, key=27)
        case "Normal":
            ser_tp_dis_param1 = col3.number_input("mean", step=0.01, key=28)
            ser_tp_dis_param2 = col4.number_input("sd", step=0.01, key=29)
        case "Exponential":
            ser_tp_dis_param1 = col3.number_input("\u03BB", 0.01, step=0.01, key=30)
            ser_tp_dis_param2 = None

# queue behavior and stats settings
st.subheader("Queue Behavior and Stats Settings")

bulk = st.checkbox("Bulk (Customers could decide not to join the queue when \
    the length of the queue is too long)")
if bulk:
    col1, col2, col3 = st.columns(3)
    bulk_start = col1.text_input(
        "Start",
        help="The length of the queue in which probability of bulking begin \
            to increase from 0.0"
    )
    bulk_stop = col2.text_input(
        "Stop",
        help="The length of the queue in which further increasing will have \
            no effect on probability of bulking"
    )
    bulk_half = col3.text_input(
        "Half",
        help="The length of the queue in which probability of bulking is 0.5"
    )

renege = st.checkbox("Renege (Customers could leave the queue if they've \
    been waiting for too long in the queue)")
if renege:
    col1, col2, col3 = st.columns(3)
    renege_start = col1.text_input(
        "Start",
        help="The time spent in the queue in which probability of reneging \
            begin to increase from 0.0"
    )
    renege_stop = col2.text_input(
        "Stop",
        help="The time spent in the queue in which further increasing will\
            have no effect on probability of reneging"
    )
    renege_half = col3.text_input(
        "Half",
        help="The length of the queue in which probability of reneging is 0.5"
    )

col1, col2, col3 = st.columns([2, 1, 1])
discipline = col1.selectbox(
        "Queue behavior discipline",
        ["FIFO", "LIFO", "SIRO"]
)
t_star = col2.number_input(
    "t*",
    1,
    step=1,
    help="Used in Statistics: proportion of customers delayed in the queue \
        more than t* time"
)
t_star = col3.number_input(
    "t*",
    1,
    step=1,
    help="Used in Statistics: proportion of time in which the queue contained \
        more than k* customers"
)
# simulation
st.header("Simulation")

if 'simulation' not in st.session_state:
    st.session_state.simulation = 0


def set_state(state):
    st.session_state.simulation = state


if st.session_state.simulation == 0:
    st.write("")
    st.button(
        "Start Simulation", type="primary", on_click=set_state, args=[1]
    )

if st.session_state.simulation == 1:
    st.write("")
    st.button(
        "Pause", type="primary", on_click=set_state, args=[0]
    )
