# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        states = self.mdp.getStates()
        for iter in range(self.iterations):
            newValues = util.Counter()

            nonTerminalStates = [state for state in states if not self.mdp.isTerminal(state)]

            for state in nonTerminalStates:
                possibleActionValues = []
                possibleActions = self.mdp.getPossibleActions(state)

                for action in possibleActions:
                    value = self.computeQValueFromValues(state, action)
                    possibleActionValues.append(value)

                maxValue = max(possibleActionValues)
                newValues[state] = maxValue

            self.values = newValues



    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        transitionStates = self.mdp.getTransitionStatesAndProbs(state, action)
        q = 0

        for ts in transitionStates:
            r = self.mdp.getReward(state, action, ts[0])
            t = ts[1]
            v = self.values[ts[0]]
            q += t * (r + self.discount * v)

        return q

        util.raiseNotDefined()

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """

        possibleActions = []

        for action in self.mdp.getPossibleActions(state):
            value = self.computeQValueFromValues(state, action)
            possibleActions.append((action, value))


        if(len(possibleActions) == 0):
            return None
        else:
            possibleActions.sort(key = lambda x: x[1], reverse = True)
            return possibleActions[0][0]

        util.raiseNotDefined()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states = self.mdp.getStates()

        for iter in range(self.iterations):
            stateIndex = iter % len(states)

            state = states[stateIndex]

            if not self.mdp.isTerminal(state):
                possibleActionValues = []
                possibleActions = self.mdp.getPossibleActions(state)

                for action in possibleActions:
                    value = self.computeQValueFromValues(state, action)
                    possibleActionValues.append(value)

                maxValue = max(possibleActionValues)
                self.values[state] = maxValue


class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        # Compute predecessors of all states.property
        predecessors = {}
        states = self.mdp.getStates();

        for state in states:
            for action in self.mdp.getPossibleActions(state):
                for successor in self.mdp.getTransitionStatesAndProbs(state, action):

                    if successor[0] not in predecessors:
                        predecessors[successor[0]] = {state}
                    else:
                        predecessors[successor[0]].add(state)

        #print(str(predecessors))

        # Initialize an empty priority queue.
        pq = util.PriorityQueue()
        nonTerminalStates = [state for state in states if not self.mdp.isTerminal(state)]

        newValues = util.Counter()

        # For each non-terminal state s, do: (note: to make the autograder work for this question, you must iterate over states in the order returned by self.mdp.getStates())
        for state in nonTerminalStates:
            # Find the absolute value of the difference between the current value of s in self.values and the highest Q-value across all possible actions from s (this represents what the value should be); call this number diff. Do NOT update self.values[s] in this step.
            qValues = []
            possibleActions = self.mdp.getPossibleActions(state)

            for action in possibleActions:
                value = self.computeQValueFromValues(state, action)
                qValues.append(value)

            #newValues[state] = maxValue
            diff = abs(self.values[state] - max(qValues))#newValues[state])
            # Push s into the priority queue with priority -diff (note that this is negative). We use a negative because the priority queue is a min heap, but we want to prioritize updating states that have a higher error.
            pq.update(state, -diff)

        # For iteration in 0, 1, 2, ..., self.iterations - 1, do:
        for iter in range(self.iterations):
            # If the priority queue is empty, then terminate.
            if pq.isEmpty():
                return
            # Pop a state s off the priority queue.
            s = pq.pop()
            # Update the value of s (if it is not a terminal state) in self.values.
            if not self.mdp.isTerminal(s):
                possibleActionValues = []
                possibleActions = self.mdp.getPossibleActions(s)

                for action in possibleActions:
                    value = self.computeQValueFromValues(s, action)
                    possibleActionValues.append(value)

                self.values[s] = max(possibleActionValues)
            # For each predecessor p of s, do:
            for p in predecessors[s]:
                # Find the absolute value of the difference between the current value of p in self.values and the highest Q-value across all possible actions from p (this represents what the value should be); call this number diff. Do NOT update self.values[p] in this step.
                possibleActionValues = []
                possibleActions = self.mdp.getPossibleActions(p)

                for action in possibleActions:
                    value = self.computeQValueFromValues(p, action)
                    possibleActionValues.append(value)

                maxValue = max(possibleActionValues)
                diff = abs(self.values[p] - maxValue)
                # If diff > theta, push p into the priority queue with priority -diff (note that this is negative), as long as it does not already exist in the priority queue with equal or lower priority. As before, we use a negative because the priority queue is a min heap, but we want to prioritize updating states that have a higher error
                if diff > self.theta:
                    pq.update(p, -diff)
