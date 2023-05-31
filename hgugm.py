import queueing_tool as qt
import networkx as nx
import numpy as np

from priority_seize_agent import PrioritySeizeAgent
from custom_ordering_queue import CustomOrderingQueue
from by_order_queue_server import CustomOrderingQueueServer

# queue priority: https://github.com/djordon/queueing-tool/issues/67


# FUNCTIONS FOR ARRIVAL AND SERVING DISTRIBUTIONS.
def rate(t):
    return 25 + 350 * np.sin(np.pi * t / 2)**2


def arr_f(t):
    return qt.poisson_random_measure(t, rate, 375)


def ser_f(t):
    return t + np.random.exponential(0.2 / 2.1)


# Defining nodes
AMOUNT_OF_SURGICAL_ROOMS = 3
AMOUNT_OF_URPA_BEDS = 10
emergency_patients_waiting_room = 0
programmed_patients_waiting_room = 1
ambulatory_patients_waiting_room = 2
presurgical_waiting_room = 3
preurpa_waiting_room = 4
exit = 5

# Creating the graph.

adja_list = {emergency_patients_waiting_room: [presurgical_waiting_room],
             programmed_patients_waiting_room: [presurgical_waiting_room],
             ambulatory_patients_waiting_room: [presurgical_waiting_room],
             presurgical_waiting_room: [preurpa_waiting_room],
             preurpa_waiting_room: [exit]}

TYPE_INCOMING_QUEUE = 1
TYPE_SURGICAL_ROOM_QUEUE = 2
TYPE_URPA_QUEUE = 3
edge_list = {emergency_patients_waiting_room: {presurgical_waiting_room: TYPE_INCOMING_QUEUE},
             programmed_patients_waiting_room: {presurgical_waiting_room: TYPE_INCOMING_QUEUE},
             ambulatory_patients_waiting_room: {presurgical_waiting_room: TYPE_INCOMING_QUEUE},
             presurgical_waiting_room: {preurpa_waiting_room: TYPE_SURGICAL_ROOM_QUEUE},
             preurpa_waiting_room: {exit: TYPE_URPA_QUEUE}}

g = qt.adjacency2graph(adjacency=adja_list, edge_type=edge_list)

# Creating the network.
queue_server_with_priorities = CustomOrderingQueueServer(
    sorter=lambda x: x.key)
# q_classes = {1: qt.QueueServer, 2: qt.QueueServer}
q_classes = {1: qt.QueueServer, 2: qt.QueueServer}
q_args = {
    TYPE_INCOMING_QUEUE: {
        'arrival_f': arr_f,
        'service_f': lambda t: t,
        'AgentFactory': PrioritySeizeAgent

    },
    TYPE_SURGICAL_ROOM_QUEUE: {
        'num_servers': AMOUNT_OF_SURGICAL_ROOMS,
        'service_f': ser_f
    },
    TYPE_URPA_QUEUE: {
        'num_servers': AMOUNT_OF_URPA_BEDS,
        'service_f': ser_f
    }
}

qn = qt.QueueNetwork(g=g, q_classes=q_classes, q_args=q_args, seed=13)


# Initializing which nodes receives agents
qn.initialize(edge_type=TYPE_INCOMING_QUEUE)

# Simulating till t=xxx seconds. We get information about all queues and agent arrival, departure and service start time:
qn.start_collecting_data()
qn.simulate(t=2.5)
print("Number of events:" + str(qn.num_events))
queue_data = qn.get_queue_data()
# COLUMNS: arrival time | enter service time | departure time | length of the queue | number of agents in the queue| edge index of queue.
print(queue_data[0:2])

agents_data = qn.get_agent_data()
# print(agents_data.keys())
# for agent in agents_data.keys():
#     print(agents_data[agent])
print(agents_data[(0, 1)])


# Plotting...
# Placing edges to make it easy to see
qn.g.new_vertex_property('pos')

pos = {}

for v in qn.g.nodes():
    if v == programmed_patients_waiting_room:
        pos[v] = [0.8, 0]
    if v == ambulatory_patients_waiting_room:
        pos[v] = [0.8, 0.8]
    if v == emergency_patients_waiting_room:
        pos[v] = [0.8, 1.6]
    if v == presurgical_waiting_room:
        pos[v] = [1.6, 0.8]
    if v == preurpa_waiting_room:
        pos[v] = [2.4, 0.8]
    if v == exit:
        pos[v] = [3.2, 0.8]

qn.g.set_pos(pos)


# Placing labels
qn.g.new_vertex_property('label')
labels = {}

for v in qn.g.nodes():
    if v == programmed_patients_waiting_room:
        labels[v] = "PR"
    if v == ambulatory_patients_waiting_room:
        labels[v] = "AMB"
    if v == emergency_patients_waiting_room:
        labels[v] = "EMER"
    if v == presurgical_waiting_room:
        labels[v] = "SURG"
    if v == preurpa_waiting_room:
        labels[v] = "URPA"
    if v == exit:
        labels[v] = "EXIT"

# nx.draw_networkx_labels(qn.g, pos, labels, font_size=22, font_color="whitesmoke")

# Plot
qn.draw(fname="sim.png", figsize=(12, 3), bbox_inches='tight',
        label=labels, font_size=12, font_color="whitesmoke")
qn.animate(figsize=(4, 4))
