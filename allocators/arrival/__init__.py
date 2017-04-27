# -*- coding: utf-8 -*-
import numpy as np
from collections import defaultdict, deque
import itertools

from helpers.priority_queue import PriorityQueue


class Task(object):
    def __init__(self, user, duration, demands, submit_time=0):
        self.user = user
        self.duration = duration
        self.demands = demands
        self.submit_time = submit_time
        self.finish_time = None
        self.count = Task._counter.next()

    _counter = itertools.count()

    def __hash__(self):
        return hash(self.count)

    def __eq__(self, other):
        return self.count == other.count


class Arrival(object):
    def __init__(self, capacities, num_users):
        self.num_resources = len(capacities)
        self.num_users = num_users
        self._capacities = np.array(capacities)
        self.consumed_resources = np.zeros(self.num_resources)
        self.allocations = np.zeros((self.num_users, self.num_resources))
        self.users_queues = defaultdict(deque)
        self.running_tasks = PriorityQueue()
        self.current_time = 0.0

        self.allocation_history = []

    def pick_task(self):
        raise NotImplementedError()

    def run_after_task(self):
        return

    def run_task(self):
        task = self.pick_task()
        if task is None:
            return False

        self.consumed_resources += task.demands
        self.allocations[task.user] += task.demands
        self.allocation_history.append(self.allocations.copy())
        task.finish_time = self.current_time + task.duration
        self.running_tasks.add(task, task.finish_time)
        self.run_after_task()
        return True

    def run_all_tasks(self):
        while self.run_task():
            pass

    def finish_task(self, user, task_demands, num_tasks=1):
        raise NotImplementedError()

    def simulate(self, tasks, simulation_limit=None):
        if simulation_limit is None:
            simulation_limit = np.inf
        for task in tasks:
            if task.submit_time > self.current_time:
                self.run_all_tasks()
                self._finish_tasks_until(min(simulation_limit,
                                             task.submit_time))
                self.current_time = task.submit_time
            if task.submit_time > simulation_limit:
                return
            self.users_queues[task.user].append(task)
        self._finish_tasks_until(simulation_limit)

    def _finish_tasks_until(self, next_time):
        while True:
            next_task = self.running_tasks.get_min()
            if next_task is None or next_task.finish_time > next_time:
                break
            self.finish_task(next_task.user, next_task.demands)
            self.consumed_resources -= next_task.demands
            self.allocations[next_task.user] -= next_task.demands
            self.running_tasks.pop()
            self.run_all_tasks()
