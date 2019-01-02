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
import numpy as np
from os.path import isfile
from random import sample

class PublicationMatcher:
    def __init__ (self,  authorsList, publicationList ):
        self.authorsList = authorsList
        self.publicationList = publicationList
        
        self.publicationDict = pubsList2dict(publicationList)
        self.authorsDict = authorsList2dict(authorsList)
        
        self.subGraphs = []
        self.generatePublicationGraph()
        
    
    def generatePublicationGraph(self):
        self.pubGraph = nx.Graph()
        
        for p in self.publicationList:
            pId = p.id
            self.pubGraph.add_node(pId)
            self.pubGraph.nodes[pId]["type"] = "publication"
            for auth in p.authors:
                self.pubGraph.add_edge( pId, auth.name )
                self.pubGraph.nodes[auth.name]["type"] = "author"
                
    def generateSingleAuthor2PubDict(self):
        uniqueAuthorPubs = {}
        for node in self.pubGraph.nodes:
            if self.pubGraph.nodes[node]["type"] == "publication":
                authors = list( self.pubGraph.neighbors(node) )
                if len(authors) == 1:
                    author = authors[0]
                    if not author in uniqueAuthorPubs:
                        uniqueAuthorPubs[author] = [ node ]
                    else:
                        uniqueAuthorPubs[author].append(node)
                        
        return uniqueAuthorPubs
                
    def getWeightSum(self, pubsId):
        pubSum = 0
        for pubId in pubsId:
            pubSum += self.publicationDict[pubId].size
        
        return pubSum


    def divideGraph(self, clean= True):
        
        somethingWasFound = True
        if clean:
            self.subGraphs = []
        
        while somethingWasFound:
            somethingWasFound = False
            
            for author in self.authorsList:
                name = author.name
                if name in self.pubGraph.nodes:
                    pubs = list(self.pubGraph.neighbors(name))
                    sumWeight = self.getWeightSum(pubs)
                    if sumWeight <= author.slots:
                        self.subGraphs.append( nx.Graph( self.pubGraph.subgraph( pubs + [ name ] ) ) )
                        self.pubGraph.remove_nodes_from( pubs + [ name ]  )
                        somethingWasFound = True
                        break
                
    
    def countPublicationsInMainGraph(self):
        return len(self.getAllPublicationsFromMainGraph())
    
    def getAllPublicationsFromMainGraph(self):
        pubs = []
        for node in self.pubGraph.nodes:
            if self.pubGraph.nodes[node]["type"] == "publication":
                pubs.append(node)
                
        return pubs

    
    def removeIsolatedNodes(self):
        self.pubGraph.remove_nodes_from(list(nx.isolates(self.pubGraph)))
        
    def mergeSubgraphs(self):
        for subg in self.subGraphs:
            self.pubGraph = nx.compose(self.pubGraph, subg)
            
        self.subGrahs = []
    
    def printStatus(self):
        print("Nodes: ", len(self.pubGraph.nodes))
        print("Edges: ", len(self.pubGraph.edges))
    
    def preprocessing(self):
        self.divideGraph()
        self.mergeSubgraphs()
        self.removeUnnecessaryPublications()
        self.divideGraph()
        self.mergeSubgraphs()
        self.removeIsolatedNodes()
        
    def countMaxPublicationPoints(self, publications):
        points = 0
        for pub in publications:
            points += self.publicationDict[pub].points
            
        return points
    
    def countMaxPublicationWeight(self, publications):
        points = 0
        for pub in publications:
            points += self.publicationDict[pub].size
            
        return points
    
    def generateAuthor2Publications(self):
        publications = self.getAllPublicationsFromMainGraph()
        
        authors2publications = {}
        
        for pub in publications:
            authors = self.pubGraph.neighbors(pub)
            for author in authors:
                if author in authors2publications:
                    authors2publications[author].append(pub)
                else:
                    authors2publications[author] = [ pub ]
                    
        author2publicationsNum = {}
        
        for author in authors2publications:
            author2publicationsNum[author] = len(authors2publications[author])
            
        return authors2publications, author2publicationsNum
    
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
            data = { "maxPoints" : -flowCost/100, "maxSlots" : maxFlow/100, "flowGraph" : flowG, "flowDict" : flowDict}
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
            
    def removeUnnecessaryPublications(self):
        """Jesli autor ma kilka publikacji o identycznej masie, ktorych laczna masa przekracza jego ilosc slotow to zostaw najcenniejsze """
        uniqueAuthor2Pubs = self.generateSingleAuthor2PubDict()
        
        for author in uniqueAuthor2Pubs:
            pubs = uniqueAuthor2Pubs[author]
    #        print(author, workersDict[author].slots)
            weight2pubs = {}
            for pubId in pubs:
                newWeight = self.publicationDict[pubId].size
                if not newWeight in weight2pubs:
                    weight2pubs[newWeight] = [ pubId ]
                else:
                    weight2pubs[newWeight].append(pubId)
                    
            for weight in weight2pubs:
                weightFloat = float(weight)
                pubsNo = len(weight2pubs[weight])
                
                if weightFloat*pubsNo > self.authorsDict[author].slots:
                    n = ( weightFloat*pubsNo -self.authorsDict[author].slots ) / weightFloat
                    n = int(n)
                    print("cos do usuniecia", author, n, pubsNo, weight,self.authorsDict[author].slots)
                    
                    interestingPubs = [ self.publicationDict[pubId] for pubId in weight2pubs[weight] ]
                    interestingPubs = sorted( interestingPubs, key=lambda x: x.points)
                    
                    pointReference = interestingPubs[n+1].points
                    print("najgorsza z najlepszych", pointReference)
                    
                    print([ip.points for ip in interestingPubs])
                    interestingPubs = interestingPubs[ : int(n) ]
                    
                    for ip in interestingPubs:
                        print("usuwam ", ip.points)
                        self.pubGraph.remove_node(ip.id)
                        
                    
                    otherPubs = self.pubGraph.neighbors( author )
                    otherPubs = set(otherPubs) - set(pubs)
                    
                    for op in otherPubs :
                        if self.publicationDict[ op].size == weight and self.publicationDict[ op].points <= pointReference:
#                            print("usuwam krawedz",self.publicationDict[ op].size, self.publicationDict[ op].points )
                            self.pubGraph.remove_edge(author, op)
        
    
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
        
    
def pubsList2dict( pubsList):
    pubDict = {}
    
    for pub in pubsList:
        pubDict[pub.id] = pub
        
    return pubDict

def authorsList2dict( authorsList ):
    workersDict = {}
    for  w in authorsList:
        workersDict[w.name] = w
        
    return workersDict
