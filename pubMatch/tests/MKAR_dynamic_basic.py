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
    
#workersList = readAuthors("../data/adamczykGroup.xls")
workersList = readAuthors("../data/pracownicy.xls")
publicationsList = readPublications("../data/publikacje.xls", workersList)

mkar = MKAR_DynamicProgramming(workersList, publicationsList)
mkar_flow = MKAR_FlowTheory([], [])
mkar_flow.copyFromMKAR(mkar)
print("Start")
print(mkar_flow.solveFlowProblem())

#plotGraph(mkar)
print("pierwszy preprocessing")
mkar.preprocessing()
print("Dynamicznie:")
mkar.useSimpleKnapsackSolution()
print("Dynamiczne skonczone")
mkar.preprocessing()
#mkar.useSimpleKnapsackSolution()
#mkar.preprocessing()
#plotGraph(mkar)
mkar_flow.copyFromMKAR(mkar)

print(mkar_flow.solveFlowProblem())