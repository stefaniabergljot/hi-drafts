import random
import numpy as np
from scipy.stats import poisson
import math

noLocations = 3
noBikes = 15

#state = {}
flowProbabilities = {}
values = {}
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
    #state = {}
    #for location in range(noLocations):
    #    state[location] = 0
    #for i in range(noBikes):
    #    location = random.randint(0, noLocations - 1)
    #    state[location] += 1
    #return state

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
    #print(tup)
    #startLocation, endLocation = nextLocationWithKarma(locationTuples, allLocationTuples)
    flow = poisson.rvs(flowProbabilities[startLocation, endLocation])
    actualFlow = min(flow, currentState[startLocation])
    newState[startLocation] = currentState[startLocation] - actualFlow
    newState[endLocation] = currentState[endLocation] + actualFlow
    if newState[0]+newState[1]+newState[2] != noBikes:
        print("Bad state!")
    updateValue(currentState, newState, actualFlow)
    state = newState
    return state, locationTuples

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
    #print(len(locationTuples))
    return locationTuples.pop(random.randint(0, len(locationTuples) - 1)), locationTuples

totalValue = {}
def updateValue(state, newState, value):
    prev = getValue(state)
    prevNewStateValue = getValue(newState)
    newValue = prev * (1-heat) + (value + discount * prevNewStateValue) * heat
    values[str(state)] = newValue
    if str(state) not in visited:
        visited[str(state)] = 0
        totalValue[str(state)] = 0
    totalValue[str(state)] += value + discount * prevNewStateValue
    visited[str(state)] += 1

def getValue(state):
    if str(state) not in visited:
        return 0
    return totalValue[str(state)]/visited[str(state)]
    #if str(state) not in values:
    #    values[str(state)] = 0
    #return values[str(state)]

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


print(len(values))
#for i in values:
#    reverseValues[values[i]] = i
    #print(i + " :" + str(values[i]) + " \t(" + str(visited[i]) + ")")
#keys = list(reverseValues.keys())
#keys.sort(reverse=True)
# #for i in keys:
#    print(str(reverseValues[i]) + " : " + str(i) + "\t (" + str(visited[reverseValues[i]]) + ")\t or \t" + str(totalValue[str(reverseValues[i])]/visited[str(reverseValues[i])]))
#    indexedByValue[totalValue[str(reverseValues[i])]/visited[str(reverseValues[i])]] = str(reverseValues[i])
# alternatively
reverseValues = {}
indexedByValue = {}

print("-----------------------------------------")
outcomes = []
for state in totalValue:
    outcomes.append(str(getValue(state)) + " : " + str(state))
outcomes.sort(reverse=True)
for i in outcomes:
    print(i)
#valueKeys = list(indexedByValue.keys())
#valueKeys.sort(reverse=True)
#for i in valueKeys:
#    print(str(i) + " " + str(indexedByValue[i]))