import streamlit as st

st.set_page_config(
    page_title="Queue Simulation",
    menu_items={
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# title
st.title("Queue Simulation")

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
    ["Constant", "Continuous Uniform", "Normal", "Exponential"]
)

parm1, parm2 = "", ""
match arrival_distribution:
    case "Constant":
        parm1 = "c"
    case "Continuous Uniform":
        parm1 = "a"
        parm2 = "b"
    case "Normal":
        parm1 = "m"
        parm2 = "s"
    case "Exponential":
        parm1 = "\u03BB"
arr_dis_val1 = col2.text_input(parm1)
arr_dis_val2 = None
if parm2:
    arr_dis_val2 = col3.text_input(parm2)

arrival_batches = st.checkbox("Arrival could be in batch")
if arrival_batches:
    col1, col2, col3 = st.columns([2, 1, 1])
    arrival_batch_distribution = col1.selectbox(
        "Batch Size Distribution",
        ["Constant", "Discrete Uniform", "Normal", "Poisson"]
    )
    parm1, parm2 = "", ""
    match arrival_batch_distribution:
        case "Constant":
            parm1 = "c"
        case "Discrete Uniform":
            parm1 = "a"
            parm2 = "b"
        case "Normal":
            parm1 = "m"
            parm2 = "s"
        case "Poisson":
            parm1 = "p"
    arr_batch_dis_val1 = col2.text_input(parm1, key=1)
    arr_batch_dis_val2 = None
    if parm2:
        arr_batch_dis_val2 = col3.text_input(parm2, key=2)

# service settings
st.subheader("Service Settings")

col1, col2, col3 = st.columns([2, 1, 1])

service_distribution = col1.selectbox(
    "Service Time Distribution",
    ["Constant", "Continuous Uniform", "Normal", "Exponential"]
)

parm1, parm2 = "", ""
match service_distribution:
    case "Constant":
        parm1 = "c"
    case "Continuous Uniform":
        parm1 = "a"
        parm2 = "b"
    case "Normal":
        parm1 = "m"
        parm2 = "s"
    case "Exponential":
        parm1 = "\u03BB"
ser_dis_val1 = col2.text_input(parm1, key=3)
ser_dis_val2 = None
if parm2:
    ser_dis_val2 = col3.text_input(parm2, key=4)

service_batches = st.checkbox("Server could service to batch")
if service_batches:
    col1, col2, col3 = st.columns([2, 1, 1])
    service_batch_distribution = col1.selectbox(
        "Batch Size Distribution",
        ["Constant", "Discrete Uniform", "Normal", "Poisson"],
        key=5
    )
    parm1, parm2 = "", ""
    match service_batch_distribution:
        case "Constant":
            parm1 = "c"
        case "Discrete Uniform":
            parm1 = "a"
            parm2 = "b"
        case "Normal":
            parm1 = "m"
            parm2 = "s"
        case "Poisson":
            parm1 = "p"
    ser_batch_dis_val1 = col2.text_input(parm1, key=6)
    ser_batch_dis_val2 = None
    if parm2:
        ser_batch_dis_val2 = col3.text_input(parm2, key=7)

select_randomly = st.checkbox("Server could select customers randomly")
if select_randomly:
    col, _ = st.columns(2)
    select_randomly_probability = col.text_input("Probability of a server\
        select customer randomly")

ser_dependency = st.checkbox("Service time would depend on length of queue")
if ser_dependency:
    col1, col2, col3 = st.columns(3)
    ser_dep_start = col1.text_input("Dependency starts at length of")
    ser_dep_stop = col2.text_input("and stops at length of")
    ser_dep_half = col3.text_input("Service time would be half at length of")

priority_customer = st.checkbox("Some Customers would have priority in\
    receiving service")
if priority_customer:
    col1, col2, col3, col4 = st.columns([3.5, 4, 1, 1])
    priority_probability = col1.text_input("Probability of a customer\
        having priority")
    service_time_priority_distribution = col2.selectbox(
        "Service Time of Priority Customers Distribution",
        ["Constant", "Continuous Uniform", "Normal", "Poisson"],
    )
    parm1, parm2 = "", ""
    match service_time_priority_distribution:
        case "Constant":
            parm1 = "c"
        case "Continuous Uniform":
            parm1 = "a"
            parm2 = "b"
        case "Normal":
            parm1 = "m"
            parm2 = "s"
        case "Poisson":
            parm1 = "p"
    ser_time_pri_dis_val1 = col3.text_input(parm1, key=8)
    ser_time_pri_dis_val2 = None
    if parm2:
        ser_time_pri_dis_val2 = col4.text_input(parm2, key=9)

# queue behavior and stats settings
st.subheader("Queue Behavior and Stats Settings")

bulk = st.checkbox("Bulk (Customers could decide not to join the queue when \
    length of the queue is too long)")
if bulk:
    col1, col2, col3 = st.columns([1, 1, 2])
    bulk_start = col1.text_input("Bulk starts at length of")
    bulk_stop = col2.text_input("and stops at length of", key=10)
    bulk_half = col3.text_input("Probability of bulking would be half at\
        length of")

renege = st.checkbox("Renege (Customers could leave the queue when they've \
    been waiting for too long in the queue)")
if renege:
    col1, col2, col3 = st.columns([1, 1, 2])
    renege_start = col1.text_input("Renege starts at time of")
    renege_stop = col2.text_input("and stops at time of", key=11)
    renege_half = col3.text_input("Probability of reneging would be half at\
        time of")

col1, col2, col3 = st.columns([2, 1, 1])
discipline = col1.selectbox(
        "Queue behavior discipline",
        ["FIFO", "LIFO", "SIRO"]
    )
t_star = col2.number_input("t*", 1, step=1, help="Used for the ratio of \
    customers who spend more than t* time in the queue to all customers")
k_star = col3.number_input("k*", 1, step=1, help="Used for the ratio of \
    the times which the length of the queue is more than k* to all times")

st.write(" ")
running = st.button("Start Simulation", type="primary")
