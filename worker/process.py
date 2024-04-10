import multiprocessing
import queue

import state
from .network import NetworkThread
from .handler import HandlerThread
from .worker_socket import WorkerSocket
from .context import WorkerContext
from .history import History
from .metrics import Metrics


class WorkerProcess(multiprocessing.Process):
    def __init__(self, count, process_id, gtl, el, shared_el, results_directory, k, sorted_neighbors, fid_to_dist, is_cluster):
        super(WorkerProcess, self).__init__()
        self.history = History(1)
        self.metrics = Metrics(self.history, results_directory)
        self.context = WorkerContext(
            count, process_id, gtl, el, shared_el, self.metrics, k, sorted_neighbors, fid_to_dist, is_cluster)
        self.sock = WorkerSocket()
        self.is_cluster = is_cluster

    def run(self):
        event_queue = queue.Queue()
        state_machine = state.StateMachine(self.context, self.sock, self.metrics, state.EuclideanWeightPolicy(), event_queue, self.is_cluster)

        network_thread = NetworkThread(event_queue, self.context, self.sock)
        handler_thread = HandlerThread(event_queue, state_machine, self.context)
        network_thread.start()
        handler_thread.start()

        network_thread.join()
        handler_thread.join()
