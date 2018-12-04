#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 14:46:58 2018

@author: michal
"""

from IOtemp import readAuthors, readPublications
from publicationMatcher import PublicationMatcher
import networkx as nx

def printSolution( solution ):
    for p in solution.publication2authors:
        print( p, solution.publication2authors[p])
        
def checkN(workersList):
    N = 0
    for w in workersList:
        N += w.time
        
    return N/4
        
workersList = readAuthors("pracownicy.xls")
publicationsList = readPublications("publikacje.xls", workersList)

pm = PublicationMatcher(workersList, publicationsList)
pm.printStatus()
#pm.preprocessing()
pm.printStatus()

pubs = pm.getSortedPublicationByPoints()
flowG = pm.buildFlowGraph(pubs)
maxFlow, flowDict = nx.maximum_flow(flowG, "s", "t")
print(maxFlow)
print(checkN(workersList))
#for node1 in flowDict:
#    for node2 in flowDict[node1]:
#        if node1 == "t" or node2 == "t":
#            print(node1, node2, flowDict[node1][node2])
#solution = pm.branchAndBound(258, 7900, pubs)
#if solution:
#    printSolution(solution)
#else:
#    print("nic ni ma")