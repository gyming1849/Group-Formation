import json
import os
import random
import time

import numpy as np
from message import Message, MessageTypes
from config import Config
from .types import StateTypes
from worker.network import PrioritizedItem
from itertools import combinations
from utils import write_json, dict_hash


class StateMachine:
    def __init__(self, context, sock, metrics, weight_policy, event_queue, is_cluster):
        self.state = None
        self.context = context
        self.metrics = metrics
        self.sock = sock
        self.event_queue = event_queue
        self.last_neighbors_hash = None
        self.eta = Config.ETA
        self.is_neighbors_processed = False
        self.solution_eta_idx = -1
        self.max_eta_idx = -1
        self.num_heuristic_invoked = 0
        self.last_expanded_time = 0
        self.last_h_ran_time = 0
        self.solution_range = 0
        self.sorted_neighbor_fids = []
        self.weight_policy = weight_policy
        self.is_cluster = is_cluster
        self.clock = 0
        self.choose_ctx = None
        if not is_cluster:
            self.clock = 3

    def get_w(self):
        return self.context.w

    def get_c(self):
        return self.context.c

    def set_w(self, w):
        self.context.w = w

    def set_c(self, c):
        self.context.c = c

    def get_w_v(self, c):
        return self.weight_policy.compute(c, self.context.fid, self.context.el, self.context.neighbors)

    def is_proper_v(self, c):
        new_w = self.get_w_v(c)
        weights = [self.context.neighbors[i].w for i in c]
        return all([new_w >= w for w in weights])

    def attr_v(self, c):
        return self.get_w_v(c) if self.is_proper_v(c) else (-1,)

    def start(self):
        self.context.deploy()
        self.enter(StateTypes.SINGLE)

    def handle_discover(self, msg):
        pass

    def set_pair(self, c):
        w = self.get_w_v(c)
        # if w != self.get_w():
        self.set_c(c)
        self.set_w(w)
        self.context.set_pair()

    def handle_stop(self, msg):
        stop_msg = Message(MessageTypes.STOP).to_all()
        self.broadcast(stop_msg)
        self.cancel_timers()

        if not Config.DEBUG:
            min_fid = min(self.get_c() + (self.context.fid,))

            if len(self.get_c()):
                dists = []
                count = 0
                els = [self.context.el] + [self.context.neighbors[i].el for i in self.get_c()]
                for el_i, el_j in combinations(els, 2):
                    dists.append(np.linalg.norm(el_i - el_j))
                    count += 1
            else:
                dists = [0]
                count = 1
                els = [self.context.el]

            if Config.H == 2.1 or Config.H == 'canf':
                m_range = self.context.radio_range
                s_range = self.solution_range
            else:
                m_range = -1
                s_range = -1
            results = {
                # "5 weight": self.get_w()[0],
                "0 clique members": self.get_w()[1:],
                # "6 dist between each pair": dists,
                # "7 coordinates": [list(el) for el in els],
                "1 min dist": min(dists),
                "1 avg dist": sum(dists) / count,
                "1 max dist": max(dists),
                # "4 total dist": sum(dists),
                "2 max eta": self.max_eta_idx + 1,
                "2 solution eta": self.solution_eta_idx + 1,
                "3 max range": m_range,
                "3 solution range": s_range,
                "3 number of requested expansions": self.context.num_expansions,
                "3 number of neighbor driven expansions": self.context.num_neighbor_expansions,
                "4 h invoked": self.num_heuristic_invoked,
                "5 queue size": self.event_queue.qsize(),
            }
            results.update(self.metrics.get_final_report_())
            write_json(self.context.fid, results, self.metrics.results_directory, self.context.fid == min_fid)

            if Config.TIMELINE_LOG:
                with open(os.path.join(self.metrics.results_directory, f'nt_{self.context.fid}.n.json'), "w") as f:
                    json.dump(self.metrics.network_timeline, f)

                with open(os.path.join(self.metrics.results_directory, f'ht_{self.context.fid}.h.json'), "w") as f:
                    json.dump(self.metrics.heuristic_timeline, f)

        if Config.DEBUG:
            if len(self.get_c()):
                print(f"{self.context.fid} is paired with {self.get_c()} w={self.get_w()}"
                      f" num_heuristic_invoked={self.num_heuristic_invoked}")

            else:
                print(f"{self.context.fid} is single num_heuristic_invoked={self.num_heuristic_invoked}")

    def sort_neighbors(self):
        if Config.OPT_SORT:
            if len(self.context.neighbors) != len(self.sorted_neighbor_fids):
                self.sorted_neighbor_fids = sorted(self.context.neighbors.keys(),
                                                   key=lambda x: np.linalg.norm(
                                                       self.context.neighbors[x].gtl - self.context.gtl))
        else:
            self.sorted_neighbor_fids = sorted(self.context.neighbors.keys(),
                                               key=lambda x: np.linalg.norm(
                                                   self.context.neighbors[x].gtl - self.context.gtl))

    def expand_range(self):
        timestamp = time.time()
        if timestamp - self.last_expanded_time > Config.EXPANSION_TIMEOUT:
            self.context.double_range()
            self.last_expanded_time = timestamp

    def enter(self, state):
        self.state = state
        if self.is_cluster:
            if state == StateTypes.CLUSTER_RECEIVE:
                discover_msg = Message(MessageTypes.CLUSTER_POS).to_all()
                self.broadcast(discover_msg)
            else:
                flag = self.context.calc_new_position()
                # if pos is not None:
                    # self.context.move(self.context.calc_new_position())
                # self.context.clear_neighbor()
                self.state = StateTypes.CLUSTER_RECEIVE
        else:
            if state == StateTypes.CLUSTER_RECEIVE:
                self.choose_ctx = self.context.choose_cluster()
                self.state = StateTypes.SINGLE
            if self.choose_ctx is not None:
                choose_msg = Message(MessageTypes.NODE_POS).to_fls(self.choose_ctx)
                self.broadcast(choose_msg)
                self.context.clear_neighbor()
        # if self.state == StateTypes.SINGLE:
        #     self.enter_single_state_with_heuristic()
        #     self.put_state_in_q(MessageTypes.REENTER_SINGLE_STATE)

    def drive(self, msg):
        event = msg.type
        if event == MessageTypes.NODE_POS or event == MessageTypes.CLUSTER_POS:
            flag = self.context.update_neighbor(msg)
            if self.clock >= 5 and self.is_cluster is False:
                if self.choose_ctx is None or (msg.fid == self.choose_ctx and flag is False):
                    self.enter(StateTypes.CLUSTER_RECEIVE)

        if event == MessageTypes.TIME_CLOCK:
            self.clock += 1
            if self.is_cluster:
                if self.clock >= 24:
                    self.enter(StateTypes.SINGLE)
                    self.clock = 0
                else:
                    self.enter(StateTypes.CLUSTER_RECEIVE)
            else:
                # print(self.clock)
                if self.clock >= 6:
                    self.enter(StateTypes.SINGLE)
                    self.clock = 0


        if event == MessageTypes.DISCOVER:
            self.handle_discover(msg)
        elif event == MessageTypes.STOP:
            self.handle_stop(msg)


    def broadcast(self, msg):
        msg.from_fls(self.context)
        length = self.sock.broadcast(msg)
        if length:
            self.context.log_sent_message(msg, length)
        else:
            self.context.log_dropped_send()

    def start_timers(self):
        pass

    def cancel_timers(self):
        pass
