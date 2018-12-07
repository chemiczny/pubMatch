#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 14:46:58 2018

@author: michal
"""

from IOtemp import readAuthors, readPublications
from publicationMatcher import PublicationMatcher

def printSolution( solution, pm ):
    for pub in solution.publication2authors:
            print("publikacja: ", pm.publicationDict[pub].title, pm.publicationDict[pub].year)
            print("autor: ", solution.publication2authors[pub])
        
def checkN(workersList):
    N = 0
    for w in workersList:
        N += w.time
        
    return N/4
        
workersList = readAuthors("pracownicy.xls")
publicationsList = readPublications("publikacje.xls", workersList)

pm = PublicationMatcher(workersList, publicationsList)
pm.printStatus()
pm.preprocessing()
pm.printStatus()

solution = pm.branchAndBoundHeuristic(258, 7400, 25000000 )

if solution:
    printSolution(solution)
else:
    print("Solution not found")