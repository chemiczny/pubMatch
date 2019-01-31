#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 13:15:49 2018

@author: michal
"""
import networkx as nx
from copy import deepcopy
#import numpy as np
from solution import Solution
from random import sample

class PublicationMatcher:
    
    def primitiveMaxPointsOfRest(self, publications):
        allPointsOfRest = self.countMaxPublicationPoints(publications)
        
        result = []
        for p in publications:
            allPointsOfRest -= self.publicationDict[p].points
            result.append(allPointsOfRest)
    
        return result
    
    def maxPointsOfRestFromFlowTheory(self, publications, maxW):
        result = []
        for i in range(len(publications)):
            result.append( self.maxPointsFromFlowTheory( publications[i:], maxW ) )
            
        return result
    
    def buildFlowGraph(self, publications):
        flowG = nx.DiGraph()
        flowG.add_node("s")
        flowG.add_node("t")
        
        pubs = publications
        allAuthors = []
        for p in pubs:
            publication = self.publicationDict[p]
            flowG.add_edge("s", p , capacity = publication.size, weight = - int(publication.points /publication.size)  )
            
            authors = list(self.pubGraph.neighbors(p))
            allAuthors += authors
           
            for a in authors:
                flowG.add_edge(p, a)
                
                
        allAuthors = list(set(allAuthors))
        
        for a in allAuthors:
            flowG.add_edge(a, "t", capacity = self.authorsDict[a].slots )
        
        return flowG
    
    def maxPointsFromFlowTheory(self, publications, maxW, returnDict =False):
        W = int(100*maxW)
        
        flowG = self.buildFlowGraph(publications)
            
        maxFlow, flowDict = nx.maximum_flow(flowG, "s", "t")
        if maxFlow < W:
            W = maxFlow
        
        
        flowG.nodes["s"]["demand"] = -W
        flowG.nodes["t"]["demand"] = W
        
        flowCost, flowDict = nx.network_simplex(flowG)
        if returnDict:
            data = { "maxPoints" : -flowCost/100, "maxSlots" : W/100, "flowGraph" : flowG, "flowDict" : flowDict}
            return data
        
        return -flowCost
    
    def maxPointsIncludingSolution(self, solution, publications, maxW):
#        W = int(100*maxW)
        flowG = self.buildFlowGraph(publications)
        
        p2a = solution.publication2authors
        i = 0
        for p in p2a:
            flowG.remove_edge(p, p2a[p])
            newSink = "s" + str(i)
            newVent = "t" + str(i)
            flowG.add_node( newVent, demand = self.publicationDict[p].size )
            flowG.add_edge(p, newVent)
            
            flowG.add_node( newSink, demand = -self.publicationDict[p].size )
            flowG.add_edge( newSink, p2a[p])
            
            i+=1
            
        maxFlow, flowDict = nx.maximum_flow(flowG, "s", "t")
        if maxFlow < maxW:
            maxW = maxFlow
        
        flowG.nodes["s"]["demand"] = -maxW
        flowG.nodes["t"]["demand"] = maxW
        
        flowCost, flowDict = nx.network_simplex(flowG)
        return -flowCost
    
    def getSortedPublicationByAuthor(self):
        author2allPublications, author2pubNo = self.generateAuthor2Publications()

        author2publications = self.generateSingleAuthor2PubDict()

        publications = self.getAllPublicationsFromMainGraph()
        pubOut = []
        pubUsed = set()
        for a in author2publications:
            uniquePubs = author2publications[a]
            pubOut += uniquePubs
            pubUsed |= set(uniquePubs) 
            
            restPubs = author2allPublications[a]
            restPubs = list( set(restPubs) - pubUsed)
            
            pubOut += restPubs
            pubUsed |= set(restPubs)
            
        rest = list( set(publications) - pubUsed)
        pubOut += rest
        
        return pubOut
    
    def getSortedPublicationByPoints(self):
        publications = self.getAllPublicationsFromMainGraph()
        sortedPubObjects = sorted( self.publicationList , key=lambda x: x.points, reverse=True)
        
        outList = []
        
        for p in sortedPubObjects:
#            print( p.points)
            if p.id in publications:
                outList.append(p.id)
                
        return outList
        
    
    def branchAndBoundHeuristic(self, maxWeight, minimalPoints = 0, maxSolutionsNo = 20000, publications = [], maxPoints = []):
        minimalPoints = int(round(minimalPoints*100))
    
        if not publications:
            publications = self.getAllPublicationsFromMainGraph()
            
        maxPointsOfRest = maxPoints
        
        if not maxPoints :
            maxPoints = self.maxPointsOfRestFromFlowTheory(publications, maxWeight)
#        print(maxPoints)
        print("Maksymalne punkty z teori przeplywu - obliczone")
        print(maxPoints)
        maxWeight = int(round(maxWeight*100))
        
        minSizePerWeight = int( maxSolutionsNo/maxWeight )
        
        queue = [ Solution() ]
        pubLen = len(publications)
        
        progressFile = open("progress.log", 'w' )
        progressFile.close()
        
        inpossibleBranches = 0
        toHeavyBranches = 0
        toCheapBranches = 0
        
        bestPointsForWeight = {}
        
        for n, publication in enumerate(publications):
            
            authors = list(self.pubGraph.neighbors(publication))
            maxPointsOfRest = maxPoints[n]
            newQueue = []
            for solution in queue:
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
    #                    
                    if newSolution.actualPoints + maxPointsOfRest < minimalPoints:
                        toCheapBranches += 1
                        continue
                    
                    weight = newSolution.actualWeight
                    if weight in bestPointsForWeight:
                        if newSolution.actualPoints > bestPointsForWeight[weight]:
                            bestPointsForWeight[weight] = newSolution.actualPoints
                    else:
                        bestPointsForWeight[weight] = newSolution.actualPoints
                        
                    points = newSolution.actualPoints
                    if len(queue) > 0.5*maxSolutionsNo:
                        if bestPointsForWeight[weight] * 0.9 >  points:
                            continue
                    
                    
                    newQueue.append(deepcopy(newSolution))
                    
                if solution.actualPoints + maxPointsOfRest >= minimalPoints:
                    newQueue.append(deepcopy(solution))
                else:
                    toCheapBranches += 1
                    
                queue = newQueue
                
                if len(queue) > maxSolutionsNo:
                    newQueue = []
                    for solution in queue:
                        weight = solution.actualWeight
                        points = solution.actualPoints
                        if bestPointsForWeight[weight] * 0.9 <  points:
                            newQueue.append(solution)
                            
                    queue = newQueue
                            
                if len(newQueue) > maxSolutionsNo:
                    mass2solutions = {}
                    for solution in newQueue:
                        weight2dict = solution.actualWeight
                        if not weight2dict in mass2solutions:
                            mass2solutions[weight2dict] = [ solution ]
                        else:
                            mass2solutions[weight2dict].append(solution)
                            
                    newQueue = []
                    for mass in mass2solutions:
                        if len(mass2solutions[mass]) <= minSizePerWeight:
                            newQueue += mass2solutions[mass]
                        else:
                            newQueue += sample( mass2solutions[mass], minSizePerWeight )
                
                    queue = newQueue
            
            
            progressFile = open("progress.log", 'a' )
            progressFile.write("#########################\n")
            progressFile.write(str(float(n/pubLen)*100) +  " %  "+str(n)+"\n")
            progressFile.write("in queue: " + str(len(queue))+"\n")
            progressFile.write("impossible branches: "+ str(inpossibleBranches)+"\n")
            progressFile.write("to heavy branches: "+ str(toHeavyBranches)+"\n")
            progressFile.write("to cheap branches: "+ str(toCheapBranches)+"\n")
            progressFile.close()
            
        if not queue:
            print("nic nie znaleziono!")
            return
            
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
                
        return bestSolution
    
    def branchAndBound(self, maxWeight, minimalPoints = 0, publications = [], maxPoints = []):
        minimalPoints = int(round(minimalPoints*100))
    
        if not publications:
            publications = self.getAllPublicationsFromMainGraph()
            
        maxPointsOfRest = maxPoints
        
        if not maxPoints :
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
        
        for n, publication in enumerate(publications):
            
            authors = list(self.pubGraph.neighbors(publication))
            maxPointsOfRest = maxPoints[n]
            newQueue = []
            for solution in queue:
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
    #                    
                    if newSolution.actualPoints + maxPointsOfRest < minimalPoints:
                        toCheapBranches += 1
                        continue
                    
                    newQueue.append(deepcopy(newSolution))
                    
                if solution.actualPoints + maxPointsOfRest >= minimalPoints:
                    newQueue.append(deepcopy(solution))
                else:
                    toCheapBranches += 1
                
            queue = newQueue
            
            
            progressFile = open("progress.log", 'a' )
            progressFile.write("#########################\n")
            progressFile.write(str(float(n/pubLen)*100) +  " %  "+str(n)+"\n")
            progressFile.write("in queue: " + str(len(queue))+"\n")
            progressFile.write("impossible branches: "+ str(inpossibleBranches)+"\n")
            progressFile.write("to heavy branches: "+ str(toHeavyBranches)+"\n")
            progressFile.write("to cheap branches: "+ str(toCheapBranches)+"\n")
            progressFile.close()
            
        if not queue:
            print("nic nie znaleziono!")
            return
            
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
                
        return bestSolution
        
def countIdenticalElements( vector2test, vectorKnown):
    count = 0
    for el in vectorKnown:
        if el in vector2test:
            count +=1
            
    return count

