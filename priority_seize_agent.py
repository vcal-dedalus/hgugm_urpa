import random
from queueing_tool.queues.agents import Agent


class PrioritySeizeAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.priority = random.randint(0, 2)
        self.job_size = random.randint(10, 20)
        self.order = (self.priority, self.job_size)
        # TODO: conservar la clave original de todos los agentes: (nodo, nº de llegada). Renombrar la de prioridad y tamaño de trabajo.
