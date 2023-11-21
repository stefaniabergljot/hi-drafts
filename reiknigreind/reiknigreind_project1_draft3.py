import random
import time

import numpy as np
from scipy.stats import poisson
import math

noLocations = 5
noBikes = 12

flowProbabilities = {}
visited = {}

policyValues = {}
def setupRandomBikes():
    order = [*range(noLocations)]
    random.shuffle(order)
    rem = noBikes
    state = {}
    for i in range(noLocations):
        state[i] = 0
    for i in order:
        val = random.randint(0, rem)
        state[i] = val
        rem -= val
    if rem > 0:
        state[order[len(order) - 1]] += rem
    return state

def setupRandomProbabilities():
    for i in range(noLocations):
        for j in range(noLocations):
            flowProbabilities[(i,j)] = random.randint(2, 30)/10

def setupEvenProbabilities():
    for i in range(noLocations):
        for j in range(noLocations):
            if i != j:
                flowProbabilities[(i,j)] = 1

def setupUnevenProbabilities():
    flowProbabilities[(0, 1)] = 1
    flowProbabilities[(0, 2)] = 1
    flowProbabilities[(1, 0)] = 1
    flowProbabilities[(1, 2)] = 1
    flowProbabilities[(2, 0)] = 1
    flowProbabilities[(2, 1)] = 1
    flowProbabilities[(0, 0)] = 0
    flowProbabilities[(1, 1)] = 0
    flowProbabilities[(2, 2)] = 0

def getRandomTransitionFrom(leavingState):
    destinations = []
    probabilities = []
    for flowProbability in flowProbabilities:
        if flowProbability[0] == leavingState:
            destinations.append(flowProbability[1])
            probabilities.append(flowProbabilities[flowProbability])
    return random.choices(destinations, weights=probabilities)[0]


def randomStep(currentState, locationTuples, allLocationTuples):
    newState = currentState.copy()
    tup, locationTuples = nextLocationWithKarma(locationTuples, allLocationTuples)
    startLocation = tup[0]
    endLocation = tup[1]
    flow = poisson.rvs(flowProbabilities[startLocation, endLocation])
    actualFlow = min(flow, currentState[startLocation])
    newState[startLocation] = currentState[startLocation] - actualFlow
    newState[endLocation] = currentState[endLocation] + actualFlow
    updateValue(currentState, newState, actualFlow)
    state = newState
    return state, locationTuples

def initializeStateActionValue(state):
    if str(state) not in policyValues:
        policyValues[str(state)] = {}
        for i in range(noLocations + 1):
            policyValues[str(state)][i] = 0

def randomStepWithPolicy(currentState, locationTuples, allLocationTuples):
    newState = currentState.copy()

    # choose a random action
    action = random.randint(0, noLocations) # max value represents no action
    # random free bike from this location?
    initializeStateActionValue(currentState)
    initializeStateActionValue(newState)

    tup, locationTuples = nextLocationWithKarma(locationTuples, allLocationTuples)
    startLocation = tup[0]
    endLocation = tup[1]

    flow = poisson.rvs(flowProbabilities[startLocation, endLocation])

    if action != noLocations and newState[action] == 0:
        policyValues[str(currentState)][action] = 0
    else:
        scootersMovedByOffer = 1
        if action == noLocations: # this represents no action
            actualFlow = min(flow, currentState[startLocation])
            newState[startLocation] = currentState[startLocation] - actualFlow
            newState[endLocation] = currentState[endLocation] + actualFlow
            scootersMovedByOffer = 0
            otherNewState = newState.copy()
            updateValueActionState(currentState, action, otherNewState, actualFlow, scootersMovedByOffer)
        else: # action
            randomEndLocation = getRandomTransitionFrom(action)

            otherNewState = newState.copy()
            if otherNewState[action] > scootersMovedByOffer:
                otherNewState[action] = newState[action] - scootersMovedByOffer
                otherNewState[randomEndLocation] = newState[randomEndLocation] + scootersMovedByOffer

            actualFlow = min(flow, currentState[startLocation])
            newState[startLocation] = currentState[startLocation] - actualFlow
            newState[endLocation] = currentState[endLocation] + actualFlow

            initializeStateActionValue(otherNewState)
            updateValueActionState(currentState, action, otherNewState, actualFlow, scootersMovedByOffer)
    state = newState
    return state, locationTuples

locationTuples = []
allLocationTuples = []
for i in range(noLocations):
    for j in range(noLocations):
        if i != j:
            allLocationTuples.append((i,j))

def incrementVisited(state, action):
    initializeVisited(state)
    visited[str(state)][action] += 1

def initializeVisited(state):
    if str(state) not in visited:
        visited[str(state)] = {}
        for i in range(noLocations+1):
            visited[str(state)][i] = 0
def nextLocationWithKarma(locationTuples, allLocationTuples):
    if len(locationTuples) == 0:
        locationTuples = allLocationTuples.copy()
    elif len(locationTuples) == 1:
        return locationTuples.pop(0), locationTuples
    return locationTuples.pop(random.randint(0, len(locationTuples) - 1)), locationTuples

def updateValueActionState(currentState, action, newState, actualFlow, offerFlow):
    prevNewStateValue = getValueWithOptimalAction(newState)
    #if str(state) not in visited:
        #visited[str(state)] = 0
        #p[str(state)] = 0
    policyValues[str(currentState)][action] += actualFlow + discount * prevNewStateValue
    #visited[str(state)] += 1
    incrementVisited(currentState, action)


totalValue = {}
def updateValue(state, newState, value):
    #prev = getValue(state)
    prevNewStateValue = getValue(newState)
    #newValue = prev * (1-heat) + (value + discount * prevNewStateValue) * heat
    #values[str(state)] = newValue
    if str(state) not in visited:
        visited[str(state)] = 0
        totalValue[str(state)] = 0
    if str(state) not in totalValue:
        totalValue[str(state)] = value + discount * prevNewStateValue
    else:
        totalValue[str(state)] += value + discount * prevNewStateValue
    visited[str(state)] += 1

def getValueWithOptimalAction(state):
    if str(state) not in visited or visited[str(state)] == 0:
        return 0
    max = 0
    noVisitsForMax = 0
    if str(state) not in policyValues:
        return 0
    for val in policyValues[str(state)]:
        if policyValues[str(state)][val] > max:
            max = policyValues[str(state)][val]
            noVisitsForMax = visited[str(state)][val]
    if noVisitsForMax == 0:
        return 0
    return max / noVisitsForMax

def getActionValue(state, action):
    if str(state) not in visited:
        return 0
    return policyValues[str(state)][action]/visited[str(state)]
def getValue(state):
    if str(state) not in visited or str(state) not in totalValue:
        return 0
    return totalValue[str(state)]/visited[str(state)]

state = setupRandomBikes()
setupEvenProbabilities()
#setupUnevenProbabilities()
heat = 0.1
discount = 0.7
offerValuePercentage = 0.5
startTime = time.time()
for i in range(1000):
    print('round ' + str(i))
    state = setupRandomBikes()
    for i in range(2000):
        state, locationTuples = randomStepWithPolicy(state, locationTuples, allLocationTuples)
    print(time.time() - startTime)
print(len(policyValues))
print("-----------------------------------------")
for state in policyValues:
    actualValues = {}
    actualValues[state] = {}
    for action in policyValues[state]:
        if visited[state][action] == 0:
            actualValues[state][action] = 0
        else:
            actualValues[state][action] = policyValues[state][action]/visited[state][action]
    print(str(state) + ": \t " + str(actualValues[state]))
print(visited)
