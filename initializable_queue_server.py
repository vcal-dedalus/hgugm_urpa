from heapq import heappush, heappop

from queueing_tool.queues.queue_servers import QueueServer


class InitializableQueueServer(QueueServer):
    def __init__(self,  initial_queue: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_agents_at_same_time(num_agents=initial_queue)

    def add_agents_at_same_time(self, num_agents: int):
        if num_agents <= 0:
            return

        for agent_index in range(0, num_agents):
            self._num_total += 1
            new_agent = self.AgentFactory((self.edge[2], self._oArrivals))
            new_agent._time = self._next_ct
            heappush(self._arrivals, new_agent)
            self._oArrivals += 1
