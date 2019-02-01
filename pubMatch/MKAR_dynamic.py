#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 14:40:32 2019

@author: michal
"""

from MKAR_Base import MKAR
from copy import deepcopy
import networkx as nx

class MKAR_DynamicProgramming(MKAR):
    def __init__(self,  authorsList, publicationList ):
        MKAR.__init__(self, authorsList, publicationList)
        
    def solveKnapsackProblemForIsolatedNode(self, author, uniqueAuthor2Pubs):
        maxW = self.authorsDict[author].slots
#        maxW *= 100
        maxW = int(maxW)
#        print("maxW ", maxW)
        pubsIds = list(self.pubGraph.neighbors(author))
        
        maxN = len(pubsIds)
        if author in uniqueAuthor2Pubs:
#            print("maksymalna liczba przedmiotow:", maxN, len(uniqueAuthor2Pubs[author]), author)
            ownPublications = uniqueAuthor2Pubs[author]
        else:
            ownPublications = []
            
        solutionMatrix = [ [ 0 for i in range(maxW+1) ] for j in range(maxN+1) ]
        solutionIndexes = [ [ [] for i in range(maxW+1) ] for j in range(maxN+1) ]
        
        for n in range(1, maxN+1):
            for w in range(1, maxW+1):
                newWeight = self.publicationDict[  pubsIds[ n-1]  ].size
                newPubId = pubsIds[ n-1] 
                solutionMatrix[n][w] = solutionMatrix[n-1][w]
                solutionIndexes[n][w] = deepcopy(solutionIndexes[n-1][w])
#                if newWeight <= w and not newPubId in solutionIndexes[n-1][w - newWeight]:
                if newWeight <= w:
                    newValue = solutionMatrix[n-1][w - newWeight] + self.publicationDict[  newPubId ].points
                    if newValue > solutionMatrix[n][w] :
                        solutionMatrix[n][w] = newValue
                        solutionIndexes[n][w] = deepcopy( solutionIndexes[n-1][w - newWeight] ) + [ newPubId ]
                        
                    elif abs(newValue - solutionMatrix[n][w] ) < 0.001:
                        actualSim = countIdenticalElements(solutionIndexes[n][w], ownPublications)
                        newSim = countIdenticalElements(solutionIndexes[n-1][w - newWeight]  + [ pubsIds[ n-1] ], ownPublications)
    
                        if newSim > actualSim:
                            solutionMatrix[n][w] = newValue
                            solutionIndexes[n][w] = deepcopy( solutionIndexes[n-1][w - newWeight] ) + [ pubsIds[ n-1] ]
                        
#        print(solutionIndexes[maxN][maxW])
        maxIndexes = list(range( maxW+1))
        allSolutionInOwnPubs = True
        optimalNodes = set()
        
        for maxInd in maxIndexes:
            indexes = solutionIndexes[maxN][maxInd]
            optimalNodes |= set(indexes)
            diff = len(set(indexes)) - len(indexes)
            if diff > 0:
                print("kurwa powtorki")
        for i in optimalNodes:
#                print(self.publicationDict[i].points, self.publicationDict[i].size, i )
            if not i in ownPublications:
                allSolutionInOwnPubs = False
        
        if allSolutionInOwnPubs:
            print("Author to isolate from KP analysis ", self.authorsDict[author].name)
            print("Publication set : ", len(optimalNodes))
            print("Available slots: ", self.authorsDict[author].slots)
            return True, optimalNodes
        
        return False, optimalNodes
    
    def useSimpleKnapsackSolution(self):
        print("################################")
        print("Solving KP for every author")
        uniqueAuthor2Pubs = self.generateSingleAuthor2PubDict()
        subgraphs = []
        optimalGraphs = []
        
        for node in self.pubGraph.nodes:
            if self.pubGraph.nodes[node]["type"] == "author":
                canUpdate, optimalSolution = self.solveKnapsackProblemForIsolatedNode(node, uniqueAuthor2Pubs)
                optimalGraphs.append( [ node ] + list(optimalSolution))
                if canUpdate:
                    subgraphs.append( [ node ] + list(optimalSolution))

        g = nx.Graph()
        for sub in optimalGraphs :
            g = nx.compose(g,nx.Graph(self.pubGraph.subgraph(sub)) )    
            
        for sub in subgraphs:
            component = nx.Graph(self.pubGraph.subgraph(sub))
            self.pubGraph.remove_nodes_from(sub)
            self.pubGraph = nx.compose(self.pubGraph, component)
            
        return g    
                    
def countIdenticalElements( vector2test, vectorKnown):
    count = 0
    for el in vectorKnown:
        if el in vector2test:
            count +=1
            
    return count