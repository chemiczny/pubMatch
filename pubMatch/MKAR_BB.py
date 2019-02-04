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
        
    def prepareForBB(self, componentsSizeDecreasing = False, authorsByPubNoDecreasing = False, pubByDecrasingAuthors = False):
        self.divideGraph()
        self.components.sort( key = lambda item: len(item.nodes()) )
        
        if componentsSizeDecreasing:
            self.components.reverse()
        
        publicationsForBB = []
        interactingAuthors = []
        lightestPublication = []
        
        authorsSum = set()
        for c in self.components:
#            print("##################################################")
            authors = self.getAuthorsFromGraph(c)
            authors.sort(  key = lambda item: len( list( c.neighbors(item ) ) ) )
            
            if authorsByPubNoDecreasing:
                authors.reverse()
                
            for a in authors:
                pubs = list(c.neighbors(a))
                pubs.sort( key = lambda item: len(  set( c.neighbors(item )) - authorsSum  ) )
                
                if pubByDecrasingAuthors:
                    pubs.reverse()
                
                for p in pubs:
                    if not p in publicationsForBB:
                        publicationsForBB.append(p)
                        coauthors = list(c.neighbors(p))
                        authorsSum |= set(coauthors)
                        
                        interactingAuthors.append(list(authorsSum))
#                        print(len(authorsSum), authorsSum)
                    
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
        self.minimalPoints = minimalPoints
        minimalPoints = int(round(minimalPoints*100))

        publications, interactingAuthors, lightestWeights = self.prepareForBB(False, False, False)
            
        
#        self.maxPoints = self.maxPointsOfRestFromFlowTheory(publications, maxWeight)
        self.maxPoints = self.maxPointsForBB(publications, maxWeight)
        print("Maksymalne punkty z teori przeplywu - obliczone")
#        print(self.maxPoints)
        self.maxWeight = int(round(maxWeight*100))
        
        self.queue = [ Solution() ]
        self.pubLen = len(publications)
        
        progressFile = open("progress.log", 'w' )
        progressFile.close()
        
        self.inpossibleBranches = 0
        self.toHeavyBranches = 0
        self.toCheapBranches = 0
        self.isomorphicSolutions = 0
        
        self.heavySolutionsNo = 0
        
        self.heavySolution = Solution()
        
        self.bestPoints = 0
        
        for n, (publication, interactions, lightestWeight) in enumerate(zip(publications, interactingAuthors, lightestWeights)):
            self.branchAndBoundIteration( n, publication, interactions, lightestWeight )
            
        if not self.queue:
            print("nic nie znaleziono!")
            return
        
        self.queue.append( self.heavySolution )
            
        bestSolution = None
        bestPoints = 0
        lowestPoints = 10000
#        print("wszystkie rozwiazania: ", len(queue))
        for solution in self.queue:
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
    
    def findBoundaryForSolution(self, solution, maxPointsOfRest):
        index = int((self.maxWeight - solution.actualWeight)/100.)+1
        
        if index < len(maxPointsOfRest):
            return solution.actualPoints + maxPointsOfRest[index]

        return  solution.actualPoints + maxPointsOfRest[-1]    
    
    def branchAndBoundIteration(self, n, publication, interactions, lightestWeight ):
        solutionClasses = {}
#        interaction2weight = {}
#        interaction2
        
        timeStart = time()
        authors = list(self.pubGraph.neighbors(publication))
        maxPointsOfRest = self.maxPoints[n]
        
        for solution in self.queue:
            if solution.boundary < self.bestPoints:
                continue
            
            if solution.actualWeight + lightestWeight > self.maxWeight:
                    if self.heavySolution.actualPoints < solution.actualPoints:
                        self.heavySolution = deepcopy(solution)
                    self.heavySolutionsNo += 1
                    continue
                
            keySet, solution = createSolutionKey(solution, interactions)
                
            if not checkSolution(solutionClasses, solution, interactions):
                self.isomorphicSolutions+=1
                continue
            
            for author in authors:
                newSolution = deepcopy(solution)
                solutionPossible = newSolution.addConnection(self.authorsDict[ author], self.publicationDict[publication] )
            
                if not solutionPossible:
                    self.inpossibleBranches += 1
                    continue
##                    
                if newSolution.actualWeight > self.maxWeight:
                    self.toHeavyBranches += 1
                    continue
                
                if newSolution.actualWeight + lightestWeight > self.maxWeight:
                    if self.heavySolution.actualPoints < newSolution.actualPoints:
                        self.heavySolution = deepcopy(newSolution)
#                        self.heavySolution = newSolution
                    self.heavySolutionsNo += 1
                    continue
    

                newSolution.boundary = self.findBoundaryForSolution( newSolution, maxPointsOfRest)
                
                if newSolution.boundary < self.minimalPoints or newSolution.boundary < self.bestPoints:
                    self.toCheapBranches += 1
                    continue
                
                if newSolution.actualPoints > self.bestPoints:
                    self.bestPoints = newSolution.actualPoints
                
                keySet, newSolution = createSolutionKey(newSolution, interactions)
                
                if not checkSolution(solutionClasses, newSolution, interactions):
                    self.isomorphicSolutions+=1
                    continue
                
                if not keySet in solutionClasses:
                    solutionClasses[keySet] = deepcopy(newSolution)
                else:
                    if solutionClasses[keySet].actualPoints >= newSolution.actualPoints:
                        self.isomorphicSolutions += 1
                    else:
                        solutionClasses[keySet] = deepcopy(newSolution)
#                        solutionClasses[keySet] = newSolution

                
            solution.boundary = self.findBoundaryForSolution( solution, maxPointsOfRest)
            if solution.boundary < self.minimalPoints or solution.boundary < self.bestPoints:
                self.toCheapBranches += 1
                continue
            
#            if not checkSolution(solutionClasses, solution, interactions):
#                self.isomorphicSolutions+=1
#                continue
            
            keySet, solution = createSolutionKey(solution, interactions)
                
            if not keySet in solutionClasses:
                solutionClasses[keySet] = deepcopy(solution)
            else:
                if solutionClasses[keySet].actualPoints >= solution.actualPoints:
                    self.isomorphicSolutions += 1
                else:
                    solutionClasses[keySet] = deepcopy(solution)

            
        self.queue = list(solutionClasses.values())
        iterationTime = datetime.timedelta(seconds = time() - timeStart)
        self.writeProgress(n, len(interactions), iterationTime)
        
    def writeProgress(self, n, interactionsSize, iterationTime):
        progressFile = open("progress.log", 'a' )
        progressFile.write("#########################\n")
        progressFile.write(str(float(n/self.pubLen)*100) +  " %  "+str(n)+"\n")
        progressFile.write("in queue: " + str(len(self.queue))+"\n")
        progressFile.write("impossible branches: "+ str(self.inpossibleBranches)+"\n")
        progressFile.write("to heavy branches: "+ str(self.toHeavyBranches)+"\n")
        progressFile.write("to cheap branches: "+ str(self.toCheapBranches)+"\n")
        progressFile.write("isomorphic solutions: "+str(self.isomorphicSolutions)+"\n")
        progressFile.write("heavy solutions: "+str(self.heavySolutionsNo)+"\n")
        progressFile.write("authors-interactions: "+str(interactionsSize)+"\n")
        progressFile.write("iteration time: "+str(iterationTime)+"\n")
        progressFile.close()
        
        
    
def createSolutionKey(newSolution, interactions):
    keySet = str(newSolution.actualWeight)
    newSolution.interactions = {}
#    weights = {}
    for a in interactions:
        if a in newSolution.authors2usedSlots:
            usedSlots = newSolution.authors2usedSlots[a]
            keySet += "-"+ str(usedSlots)
            newSolution.interactions[a] = usedSlots
#            weights[a] = usedSlots
        else:
            keySet += "-0"
            newSolution.interactions[a] = 0
#            weights[a] = 0
            
#    return keySet, weights
    return keySet, newSolution

def checkSolution( solutionClasses, newSolution, interactions ):
    oldSolution2remove = []
    for solKey in solutionClasses:
        if solutionClasses[solKey].actualWeight <= newSolution.actualWeight and solutionClasses[solKey].actualPoints >= newSolution.actualPoints:
            need2removeNewSolution = solutionAWorseThanSolutionB(newSolution,  solutionClasses[solKey], interactions)
            if need2removeNewSolution:
                return False
            
        elif solutionClasses[solKey].actualWeight >= newSolution.actualWeight and solutionClasses[solKey].actualPoints <= newSolution.actualPoints:
            need2removeOldSolution = solutionAWorseThanSolutionB(  solutionClasses[solKey],newSolution, interactions)
            if need2removeOldSolution:
                oldSolution2remove.append(solKey)
               
    for sol in oldSolution2remove:
        del solutionClasses[sol]
    
    return True
        
def solutionAWorseThanSolutionB( solutionA, solutionB, interactions):
#    if solutionA.actualPoints > solutionB.actualPoints :
#        return False
#    
#    if solutionA.actualWeight < solutionB.actualWeight:
#        return False
    
    for key in solutionA.interactions:
        if solutionA.interactions[key] < solutionB.interactions[key]:
            return False

        
    return True
        
    
    