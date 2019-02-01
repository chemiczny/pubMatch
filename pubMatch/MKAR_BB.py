#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 16:53:19 2019

@author: michal
"""

from MKAR_flow import MKAR_FlowTheory
from solution import Solution
from copy import deepcopy
from time import time
import datetime

class MKAR_BranchAndBound(MKAR_FlowTheory):
    def __init__(self,  authorsList, publicationList ):
        MKAR_FlowTheory.__init__(self, authorsList, publicationList)
        
    def prepareForBB(self, componentsSizeDecreasing = False, authorsByPubNoDecreasing = False):
        self.divideGraph()
        self.components.sort( key = lambda item: len(item.nodes()) )
        
        if componentsSizeDecreasing:
            self.components.reverse()
        
        publicationsForBB = []
        interactingAuthors = []
        lightestPublication = []
        
        authorsSum = set()
        for c in self.components:
            print("##################################################")
            authors = self.getAuthorsFromGraph(c)
            authors.sort(  key = lambda item: len( list( c.neighbors(item ) ) ) )
            
            if authorsByPubNoDecreasing:
                authors.reverse()
                
            for a in authors:
                pubs = list(c.neighbors(a))
                pubs.sort( key = lambda item: len( list( c.neighbors(item )) ) )
                
                for p in pubs:
                    if not p in publicationsForBB:
                        publicationsForBB.append(p)
                        coauthors = list(c.neighbors(p))
                        authorsSum |= set(coauthors)
                        
                        interactingAuthors.append(list(authorsSum))
                        print(len(authorsSum), authorsSum)
                    
                authorsSum.remove(a)
            
        for pInd in range(len(publicationsForBB)):
            pubs = publicationsForBB[pInd:]
            
            lightestWeight = 100
            
            for p in pubs:
                newWeight = self.publicationDict[p].size
                
                if newWeight < lightestWeight:
                    lightestWeight = newWeight
                    
            lightestPublication.append( lightestWeight )
            
        print(lightestPublication)
#        for row in interactingAuthors:
#            print(len(row), row)
            
        return publicationsForBB, interactingAuthors, lightestPublication
        
    def branchAndBound(self, maxWeight, minimalPoints = 0):
        timeStart = time()
        minimalPoints = int(round(minimalPoints*100))

        publications, interactingAuthors, lightestWeights = self.prepareForBB(True, False)
            
        
        maxPoints = self.maxPointsOfRestFromFlowTheory(publications, maxWeight)
#        print(maxPoints)
        print("Maksymalne punkty z teori przeplywu - obliczone")
        print(maxPoints)
        maxWeight = int(round(maxWeight*100))
        
        queue = [ Solution() ]
        pubLen = len(publications)
        
        progressFile = open("progress.log", 'w' )
        progressFile.close()
        
        inpossibleBranches = 0
        toHeavyBranches = 0
        toCheapBranches = 0
        isomorphicSolutions = 0
        
        heavySolutionsNo = 0
        
        heavySolutions = []
        
        bestPoints = 0
        
        for n, (publication, interactions, lightestWeight) in enumerate(zip(publications, interactingAuthors, lightestWeights)):
            solutionClasses = set()
            
            authors = list(self.pubGraph.neighbors(publication))
            maxPointsOfRest = maxPoints[n]
            newQueue = []
            for solution in queue:
                if solution.boundary < bestPoints:
                    continue
                
                for author in authors:
                    newSolution = deepcopy(solution)
                    solutionPossible = newSolution.addConnection(self.authorsDict[ author], self.publicationDict[publication] )
                
                    if not solutionPossible:
                        inpossibleBranches += 1
                        continue
##                    
                    if newSolution.actualWeight > maxWeight:
                        toHeavyBranches += 1
                        continue
                    
                    if newSolution.actualWeight + lightestWeight > maxWeight:
                        heavySolutions.append(deepcopy(newSolution))
                        heavySolutionsNo += 1
                        continue
        
    
                    newSolution.boundary = newSolution.actualPoints + maxPointsOfRest
                    if newSolution.boundary < minimalPoints or newSolution.boundary < bestPoints:
                        toCheapBranches += 1
                        continue
                    
                    if newSolution.actualPoints > bestPoints:
                        bestPoints = newSolution.actualPoints
                        
                    keySet = createSolutionKey(newSolution, interactions)
#                    
                    if not keySet in solutionClasses:
                        solutionClasses.add(keySet)    
                        newQueue.append(deepcopy(newSolution))
                    else:
                        isomorphicSolutions += 1
                    newQueue.append(deepcopy(newSolution))
                    
#                print(publication)
#                print(interactions)
                solution.boundary = solution.actualPoints + maxPointsOfRest
                if solution.boundary < minimalPoints or solution.boundary < bestPoints:
                    toCheapBranches += 1
                    continue
                
                keySet = createSolutionKey(solution, interactions)
                    
                if not keySet in solutionClasses:
                    solutionClasses.add(keySet)
                    newQueue.append(deepcopy(solution))
                else:
                    isomorphicSolutions += 1
                newQueue.append(deepcopy(solution))

                
            queue = newQueue
            
            
            progressFile = open("progress.log", 'a' )
            progressFile.write("#########################\n")
            progressFile.write(str(float(n/pubLen)*100) +  " %  "+str(n)+"\n")
            progressFile.write("in queue: " + str(len(queue))+"\n")
            progressFile.write("impossible branches: "+ str(inpossibleBranches)+"\n")
            progressFile.write("to heavy branches: "+ str(toHeavyBranches)+"\n")
            progressFile.write("to cheap branches: "+ str(toCheapBranches)+"\n")
            progressFile.write("isomorphic solutions: "+str(isomorphicSolutions)+"\n")
            progressFile.write("heavy solutions: "+str(heavySolutionsNo)+"\n")
            progressFile.close()
            
        if not queue:
            print("nic nie znaleziono!")
            return
        
        queue += heavySolutions
            
        bestSolution = None
        bestPoints = 0
        lowestPoints = 10000
#        print("wszystkie rozwiazania: ", len(queue))
        for solution in queue:
            if solution.actualPoints > bestPoints:
                bestPoints = solution.actualPoints
                bestSolution = solution
            if solution.actualPoints < lowestPoints:
                lowestPoints = solution.actualPoints
                
        self.saveSolution("solution.csv", bestSolution)
        
        processingTime = time() - timeStart
        prettyTimeTaken = str(datetime.timedelta(seconds = processingTime))
        progressFile = open("progress.log", 'a' )
        progressFile.write("#########################\n")
        progressFile.write("##########FINISH#########\n")
        progressFile.write("time taken: "+str(prettyTimeTaken)+"\n")
        progressFile.write("Points: "+str(bestSolution.actualPoints)+"\n")
        progressFile.write("Size: "+str(bestSolution.actualWeight)+"\n")
        progressFile.write("#########################\n")
        progressFile.close()
        return bestSolution
    
def createSolutionKey(newSolution, interactions):
    keySet = str(newSolution.actualWeight)+"-"+str(newSolution.actualPoints)
    for a in interactions:
        if a in newSolution.authors2usedSlots:
            keySet += "-"+ str(newSolution.authors2usedSlots[a])
        else:
            keySet += "-0"
            
    return keySet