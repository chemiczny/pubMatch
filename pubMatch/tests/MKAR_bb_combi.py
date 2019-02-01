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
from MKAR_BB import MKAR_BranchAndBound
#import matplotlib.pyplot as plt

workersList = readAuthors("../data/adamczykGroup.xls")
#workersList = readAuthors("../data/pracownicy.xls")
publicationsList = readPublications("../data/publikacje.xls", workersList)

#mkar = MKAR_DynamicProgramming(workersList, publicationsList)
mkar_flow = MKAR_BranchAndBound(workersList, publicationsList)
mkar_flow.preprocessing()
#mkar_flow.copyFromMKAR(mkar)
#print("Start")
#print(mkar_flow.solveFlowProblem())
#
#while mkar.printStatus():
#    mkar.preprocessing()
#    mkar.useSimpleKnapsackSolution()
    
#mkar_flow.copyFromMKAR(mkar)
#mkar_flow.prepareForBB(True, True)
mkar_flow.branchAndBound(3, 90)