import queueing_tool as qt
import networkx as nx
import numpy as np

from priority_seize_agent import PrioritySeizeAgent
from by_order_queue_server import ByOrderQueueServer

import csv
import json

# queue priority: https://github.com/djordon/queueing-tool/issues/67
# Assuming t=minutes:
hour = 60

# FUNCTIONS FOR ARRIVAL AND SERVING DISTRIBUTIONS.
SIMULATING_TIME = 24*hour
INITIAL_OPERATIONS = 5

print("We gonna simulate " + str(SIMULATING_TIME))


def initializing_operatig_rooms(t):
    # if t < INITIAL_OPERATIONS:
    #     t+1

    return t+SIMULATING_TIME+1


# Defining nodes
AMOUNT_OF_SURGICAL_ROOMS = 3
AMOUNT_OF_URPA_BEDS = 10
emergency_patients_waiting_room = 0
programmed_patients_waiting_room = 1
ambulatory_patients_waiting_room = 2
surgical_waiting_room = 3
urpa_waiting_room = 4
exit = 5

# Creating the graph.

adja_list = {emergency_patients_waiting_room: [surgical_waiting_room],
             programmed_patients_waiting_room: [surgical_waiting_room],
             ambulatory_patients_waiting_room: [surgical_waiting_room],
             surgical_waiting_room: [urpa_waiting_room],
             urpa_waiting_room: [exit]}

TYPE_INCOMING_QUEUE = 1
TYPE_PROGRAMMED_QUEUE = 2
TYPE_SURGICAL_ROOM_QUEUE = 3
TYPE_URPA_QUEUE = 4
edge_list = {emergency_patients_waiting_room: {surgical_waiting_room: TYPE_INCOMING_QUEUE},
             programmed_patients_waiting_room: {surgical_waiting_room: TYPE_PROGRAMMED_QUEUE},
             ambulatory_patients_waiting_room: {surgical_waiting_room: TYPE_PROGRAMMED_QUEUE},
             surgical_waiting_room: {urpa_waiting_room: TYPE_SURGICAL_ROOM_QUEUE},
             urpa_waiting_room: {exit: TYPE_URPA_QUEUE}}

g = qt.adjacency2graph(adjacency=adja_list, edge_type=edge_list)

# Creating the network.
# q_classes = {1: qt.QueueServer, 2: qt.QueueServer}
q_classes = {TYPE_INCOMING_QUEUE: qt.QueueServer,
             TYPE_PROGRAMMED_QUEUE: ByOrderQueueServer,
             TYPE_SURGICAL_ROOM_QUEUE: ByOrderQueueServer,
             TYPE_URPA_QUEUE: qt.QueueServer}
q_args = {
    TYPE_INCOMING_QUEUE: {
        'arrival_f': lambda t: t+hour,
        'service_f': lambda t: t,
        'AgentFactory': PrioritySeizeAgent,
    },
    TYPE_PROGRAMMED_QUEUE: {
        'arrival_f': initializing_operatig_rooms,
        'service_f': lambda t: t,
        'AgentFactory': PrioritySeizeAgent,
        'initial_queue': INITIAL_OPERATIONS,
    },
    TYPE_SURGICAL_ROOM_QUEUE: {
        'num_servers': AMOUNT_OF_SURGICAL_ROOMS,
        'service_f': lambda t: t + hour/2
    },
    TYPE_URPA_QUEUE: {
        'num_servers': AMOUNT_OF_URPA_BEDS,
        'service_f': lambda t: t + 2 * hour
    }
}

qn = qt.QueueNetwork(g=g, q_classes=q_classes, q_args=q_args, seed=13)


# Initializing which nodes receives agents
qn.initialize(edge_type=[TYPE_INCOMING_QUEUE, TYPE_PROGRAMMED_QUEUE])

# Simulating till t=xxx seconds. We get information about all queues and agent arrival, departure and service start time:
qn.start_collecting_data()
qn.simulate(t=SIMULATING_TIME)
print("Number of events:" + str(qn.num_events))
queue_data = qn.get_queue_data()  # return_header=True)
# arrival_time, enter_service_time, departure_time, length of queue, number_of_agents, edge_index_of_queue.
np.savetxt("queue_data.csv", queue_data,
           delimiter=",", fmt='%i')
# COLUMNS: arrival time | enter service time | departure time | length of the queue | number of agents in the queue| edge index of queue.
print(queue_data[0:2])

agents_data = qn.get_agent_data()
times = []
for k in agents_data.keys():
    times.append(agents_data[k][0, 2]-agents_data[k][0, 0])

with open("agent_data.txt", "w") as f:
    for agent in agents_data.keys():
        f.write("\n\nAGENT: " + str(agent)+"\n")
        f.write(np.array2string(
            a=agents_data[agent], formatter={'float_kind': lambda x: "%.0f" % x}))
        # f.write(str((agents_data[agent])))
# print(agents_data[(0, 22)])


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
    if v == surgical_waiting_room:
        pos[v] = [1.6, 0.8]
    if v == urpa_waiting_room:
        pos[v] = [2.4, 0.8]
    if v == exit:
        pos[v] = [3.2, 0.8]

qn.g.set_pos(pos)

# Plot
# qn.draw(fname="sim.png", figsize=(12, 3), bbox_inches='tight',
#        font_size=12, font_color="whitesmoke")
qn.animate(figsize=(4, 4), t=SIMULATING_TIME)
