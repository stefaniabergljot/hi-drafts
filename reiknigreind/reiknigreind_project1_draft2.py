import random
import numpy as np
from scipy.stats import poisson
import math

noLocations = 4
noBikes = 20

flowProbabilities = {}
visited = {}

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
            flowProbabilities[(i,j)] = 1

def setupUnevenProbabilities():
    flowProbabilities[(0, 1)] = 2
    flowProbabilities[(0, 2)] = 1
    flowProbabilities[(1, 0)] = 1
    flowProbabilities[(1, 2)] = 1
    flowProbabilities[(2, 0)] = 0.5
    flowProbabilities[(2, 1)] = 0.5

def randomStep(currentState, locationTuples, allLocationTuples):
    newState = currentState.copy()
    tup, locationTuples = nextLocationWithKarma(locationTuples, allLocationTuples)
    startLocation = tup[0]
    endLocation = tup[1]
    #startLocation, endLocation = nextLocationWithKarma(locationTuples, allLocationTuples)
    flow = poisson.rvs(flowProbabilities[startLocation, endLocation])
    actualFlow = min(flow, currentState[startLocation])
    newState[startLocation] = currentState[startLocation] - actualFlow
    newState[endLocation] = currentState[endLocation] + actualFlow
    checkIfBadState(newState)
    updateValue(currentState, newState, actualFlow)
    state = newState
    return state, locationTuples

def checkIfBadState(newState):
    sum = 0
    for i in range(noLocations):
        sum += newState[i]
    if sum != noBikes:
        print("Bad state!")

locationTuples = []
allLocationTuples = []
for i in range(noLocations):
    for j in range(noLocations):
        if i != j:
            allLocationTuples.append((i,j))

def nextLocationWithKarma(locationTuples, allLocationTuples):
    if len(locationTuples) == 0:
        locationTuples = allLocationTuples.copy()
    elif len(locationTuples) == 1:
        return locationTuples.pop(0), locationTuples
    return locationTuples.pop(random.randint(0, len(locationTuples) - 1)), locationTuples

totalValue = {}
def updateValue(state, newState, value):
    prevNewStateValue = getValue(newState)
    if str(state) not in visited:
        visited[str(state)] = 0
        totalValue[str(state)] = 0
    totalValue[str(state)] += value + discount * prevNewStateValue
    visited[str(state)] += 1

def getValue(state):
    if str(state) not in visited:
        return 0
    return totalValue[str(state)]/visited[str(state)]

state = setupRandomBikes()
setupEvenProbabilities()
#setupUnevenProbabilities()
heat = 0.1
discount = 0.7
for i in range(3000):
    print('round ' + str(i))
    state = setupRandomBikes()
    for i in range(100):
        state, locationTuples = randomStep(state, locationTuples, allLocationTuples)

print("-----------------------------------------")
outcomes = []
for state in totalValue:
    outcomes.append(str(getValue(state)) + " : " + str(state) + " (visited " + str(visited[str(state)])+ " times)")
outcomes.sort(reverse=True)
for i in outcomes:
    print(i)