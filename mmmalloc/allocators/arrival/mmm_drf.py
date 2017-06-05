# -*- coding: utf-8 -*-
import numpy as np

from mmmalloc.allocators.arrival import Arrival, Task
from mmmalloc.helpers.priority_queue import PriorityQueue


# 3M_DRF
# the 3M allocation must only come into action when users already reached 1/n
# of resource utilization for their dominant resource
# there must be a separate credibility for each resource and user
class MMMDRF(Arrival):
    def __init__(self, capacities, users_resources_dict,
                 initial_credibilities=None, delta=1.0, keep_history=False):
        """
        :param capacities: array with capacities for each resource
        :param users_resources_dict: dict with users resources user:[resources]
        """
        num_users = len(users_resources_dict)

        super(MMMDRF, self).__init__(capacities, num_users, keep_history)

        users_resources = [0]*num_users
        for user, resource in users_resources_dict.iteritems():
            users_resources[Task._user_index[user]] = resource  # HACK!

        self.user_resources = np.array(users_resources)
        self.delta = delta

        self.user_resources_queue = PriorityQueue(np.zeros(self.num_users))

        if initial_credibilities is None:
            self.credibilities = np.zeros((self.num_users, self.num_resources))
        else:
            self.credibilities = np.array(initial_credibilities)

        self.user_credibilities_queue = PriorityQueue(
            np.max(self.credibilities, axis=1))  # TODO check if it makes sense

    def _insert_user_resources_heap(self, user):
        # same as wDRF when user_resources/capacities are used as the weight
        res_left = np.max(self.allocations[user]/self.user_resources[user])

        # don't bother adding when users are using more than they have (their
        # share is >= 1)
        if res_left < 1:
            self.user_resources_queue.add(user, res_left)

    def _insert_user_cred_heap(self, user):
        dominant_share = np.max((self.allocations[user] -
                                 self.user_resources[user] -
                                 self.credibilities[user]) / self._capacities)
        self.user_credibilities_queue.add(user, dominant_share)

    def _insert_user(self, user):
        self._insert_user_resources_heap(user)
        self._insert_user_cred_heap(user)

    def pick_task(self):
        def user_fulfills_request(task):
            user_alloc = self.allocations[task.user]
            return np.all(user_alloc + task.demands <= self.user_resources)

        def pick_from_resources():
            return self._pick_from_queue(self.user_resources_queue,
                                         user_fulfills_request)

        def pick_from_cred():
            return self._pick_from_queue(self.user_credibilities_queue)

        picked_task = pick_from_resources() or pick_from_cred()
        return picked_task

    def finish_task(self, task):
        self._insert_user(task.user)
        # TODO update credibilities

        # raise NotImplementedError()  # TODO here is the time to reinsert users
        # if self.consumed_resources < task_demands or \
        #    self.allocations[user] < task_demands:
        #     return
        # self.consumed_resources -= task_demands
        # self.allocations[user] -= task_demands
        # contributions = self.user_resources[user] - task_demands
        # # TODO WRONG!
        # damping = self.delta ** self._duration[user]
        # self.credibilities[user] = damping * self.credibilities[user] + \
        #                                (1-damping) * contributions
        # # update credibility and reinsert user
        # self.update(user)


# How to calculate the credibility, 3 choices:
# * I may keep using the old credibility where we have to choose what user will
#   provide each resource. This requires a queue of "donors"
# * I may give resources equally to each donor
# * I may forget about it and use the exponential moving average of the total
#   allocation (users would benefit even when nobody uses their stuff as long
#   as they are "contributing")

# When the credibility changes:
# * Every instant (being amortized)
# * Task is allocated
# * Task finishes


# == OLD IDEAS keeping for reference as some stuff are still useful ==
# Regime 1 - "private usage"
# * keep track of the minimum difference between user usage and the resources
#   they possess in proportion to the total amount of the resource.
# * allocate resource from users whose minimum difference is the greatest (this
#   can be implemented using a priority queue of minimum differences). The
#   resource with the minimum difference may not be the user dominant resource!
# * as soon as a user reaches a point where they need more resources than they
#   possess they enter the next regime.

# Regime 2 - "3M"
# Wait till all users with pending tasks are in the 2nd regime ()
# Give priority to whoever has the greatest smallest credibility share!
# smallest credibility share for user i:
#     min(credibility_vector_i/capacity_vector_i)
# ?? if we keep allocating beyond negative credibility does it work?

# Regime 3 - "pure DRF"
# If all users have their smallest credibility share zero (it can actually be
# greater than zero, as long as it is insufficient for a single task), apply
# DRF.

# ===== Credibility =====
# -- Updating --
# We update the credibility every time a task finishes.
# What and how to update? Some ideas:
# * Every time a task finishes, the user whose task finished should have their
#   credibility discounted -- maybe this is not the best time...
# * Whenever a task enters the queue -- if a user submit a lot of tasks this
# gets really outdated, so not a good idea.
# . NOTE: something to consider is that if a user is in the first regime their
# credibility can only improve, they're also not competing with the other
# users, in a credibility standpoint, every task they have is attended as soon
# as possible.
#
# -- Amortization --
# I'll implement first without amortizing the credibility. However this should
# be done at some point. The question that pops right away is: Doesn't amortize
# all credibilities require us to update all users in the queue? In fact it
# doesn't! Instead of amortizing every user credibility we multiply whatever
# updated credibility proportionally so that it virtually discounts everything
# else. Note that the actual credibility is still required but it can be
# recovered using the same factor used to multiply the credibility when it
# enters the queue.

# ===== draft =====
# * If the credibility(positive)-allocation > 0

# For a single resource we would have to allocate whoever has the best
# credibility (discount the user and reinsert).
#
# For more resources we get inspiration from DRF

#
# Now allocate resources considering users's credibility instead of their
# possesses using the same strategy as before.
# * As soon as a user reaches a point where they need more resources than their
# credibility+possesses allow

# Regime

# Note:
# this procedure should be exactly equal to DRF when all users possess the same
# amount of resources and have zero credibility