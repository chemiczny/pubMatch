#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 13:01:57 2019

@author: michal
"""

import sys
if not "../" in sys.path:
    sys.path.append('../')
    
from IOtemp import readAuthors, readPublications
from MKAR_dynamic import MKAR_DynamicProgramming
from MKAR_flow import MKAR_FlowTheory
from plotGraph import plotGraph
import matplotlib.pyplot as plt
import networkx as nx
#workersList = readAuthors("../data/adamczykGroup.xls")
workersList = readAuthors("../data/pracownicy.xls")
publicationsList = readPublications("../data/publikacje.xls", workersList)

mkar = MKAR_DynamicProgramming(workersList, publicationsList)
mkar_flow = MKAR_FlowTheory([], [])
mkar_flow.copyFromMKAR(mkar)
print("Start")
print(mkar_flow.solveFlowProblem())

i = 0
while mkar.printStatus() and i < 5:
    mkar.preprocessing()
    mkar.useSimpleKnapsackSolution()
    i += 1
    
mkar_flow.copyFromMKAR(mkar)

print(mkar_flow.solveFlowProblem())

test = mkar.useSimpleKnapsackSolution()
#plt.figure()
#layout = nx.spring_layout(test)
#nx.draw_networkx(test, layout)

publicationsIds = mkar_flow.getAllPublicationsFromMainGraph()
data = mkar_flow.maxPointsOfRestFromFlowTheory(publicationsIds, 230)

plt.figure()
plt.plot(data)