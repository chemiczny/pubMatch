#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 13:31:05 2019

@author: michal
"""
from MKAR_Base import MKAR
import networkx as nx


class MKAR_FlowTheory(MKAR):
    def __init__(self,  authorsList, publicationList ):
        MKAR.__init__(self, authorsList, publicationList)
        
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
            result.append( self.solveFlowProblem( publications[i:], maxW ) )
            
        return result
    
    def maxPointsForBB(self, publications, maxW):
        result = []
        
        for i in range(len(publications)):
            subResult = []
            publicationSubset =  publications[i:]
            maxFlow = self.getMaxFlow(publicationSubset)
            if maxFlow < maxW:
                maxW = maxFlow
                
            for i in range(int(maxW)+1):
                subResult.append(self.solveFlowProblem(publicationSubset, float(i) ))
                
            subResult.append(self.solveFlowProblem(publicationSubset, maxW ))
            
            result.append(subResult)
            
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
    
    def getMaxFlow(self, publications = [] ):
        if not publications:
            publications = self.getAllPublicationsFromMainGraph()
            
        flowG = self.buildFlowGraph(publications)
            
        maxFlow, flowDict = nx.maximum_flow(flowG, "s", "t")
        
        return maxFlow/100.
    
    def solveFlowProblem(self, publications = [], maxW = 66666666, returnDict =False):
        W = int(100*maxW)
        if not publications:
            publications = self.getAllPublicationsFromMainGraph()
            
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
    
    def solveFlowProblemWithRestrictions(self, solution, publications, maxW):
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
    
    def extractFractionalGraph(self, flowDict):
        fractionalNodes = set()
        pubIds = self.publicationDict.keys()
        for p in pubIds:
            authors = []
            if p in flowDict:
                slotsUsed = 0
                for c in flowDict[p]:
                    slotsUsed += flowDict[p][c]
                    if flowDict[p][c] > 0:
                        authors.append(c)
            else:
                slotsUsed = 0
            
            pObj = self.publicationDict[p]
            
            if slotsUsed > 0:
                authorsNo = len(authors)
                if authorsNo > 1 or slotsUsed < pObj.size:
                    for a in authors:
                        fractionalNodes.add(a)
                        for node in self.pubGraph.neighbors(a):
                            fractionalNodes.add( node) 
                        
        return self.pubGraph.subgraph(list(fractionalNodes))