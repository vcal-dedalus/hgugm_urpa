import queueing_tool as qt
from custom_ordering_queue import CustomOrderingQueue
from initializable_queue_server import InitializableQueueServer
from queueing_tool.queues.agents import Agent


class ByOrderQueueServer(InitializableQueueServer):
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = CustomOrderingQueue(
            sorter=ByOrderQueueServer.get_agent_order)

    @staticmethod
    def get_agent_order(agent: Agent):
        if hasattr(agent, "order"):
            return agent.order

        return agent.key
