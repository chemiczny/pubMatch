#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 16:08:02 2019

@author: michal
"""
from copy import deepcopy

class ItemsType:
    def __init__ (self, assignmentRestriction, initialItem ):
        self.assignmentRestriction = assignmentRestriction
        self.items = [ initialItem ]
        
class Path:
    def __init__(self, itemDict):
        self.path = []
        self.actualInteractions = set([])
        self.maxInteractions = 0
        self.interactionSum = 0
        self.interactionsHistory = []
        self.notAnalysedNodes = set( itemDict.keys() )
        
    def addItem(self, itemId, itemDict ):
        self.path.append(itemId)
        self.actualInteractions |=  itemDict[itemId].assignmentRestriction
        
        self.notAnalysedNodes.remove(itemId)
        restRestrictions = set([])
        for key in self.notAnalysedNodes:
            restRestrictions |= itemDict[key].assignmentRestriction
            
        toRemove = self.actualInteractions - restRestrictions
        for interaction in toRemove:
            self.actualInteractions.remove(interaction)
            
        interactionLen = len(self.actualInteractions)
        if interactionLen > self.maxInteractions:
            self.maxInteractions = interactionLen
            
        self.interactionSum += interactionLen
        self.interactionsHistory.append(interactionLen)
        
    def calcInteractionsWithNewNode(self, itemId, itemDict):
        tempInteractions = self.actualInteractions | itemDict[itemId].assignmentRestriction
        
        nodes = deepcopy(self.notAnalysedNodes)
        nodes.remove(itemId)
        restRestrictions = set([])
        for key in nodes:
            restRestrictions |= itemDict[key].assignmentRestriction
            
        toRemove = tempInteractions - restRestrictions
        for interaction in toRemove:
            tempInteractions.remove(interaction)
            
        return len(tempInteractions)
    
    def findPromisingNodes(self, itemDict):
        lowestInteractions = 1000
        promisingNodes = []
        
        for node in self.notAnalysedNodes:
            interLen = self.calcInteractionsWithNewNode(node, itemDict)
            if interLen < lowestInteractions:
                lowestInteractions = interLen
                promisingNodes = [ node ]
            elif interLen == lowestInteractions:
                promisingNodes.append(node)
                
        return promisingNodes
    
    def getKey(self):
        strPath = [ str(el) for el in sorted(self.path) ]
        key = "_".join( strPath )
        return key
        

class PublicationSorter:
    def __init__(self, graph, publicationList):
        self.graph = graph
        self.pubs = publicationList
        self.publicationTypes = {}
        
    def findPublicationClasses(self):
        self.publicationTypes = {}
        temp = {}
        
        for pub in self.pubs:
            authors = list(self.graph.neighbors(pub))
            authorsSet = set(authors)
            authors.sort()
            authors = "_".join(authors)
            self.graph.nodes[pub]["itemClass"]= authors
            if authors in temp:
                temp[authors].items.append(pub)
            else:
                temp[authors] = ItemsType(authorsSet, pub)
                
        for newId, key in enumerate(temp):
            self.publicationTypes[newId] = temp[key]
                
        print("wszystkie publikacje: ", len(self.pubs))
        print("liczba klas publikacji: ", len(self.publicationTypes))
        
    def sort(self, interactionLimit):
        sortedKeys = list(self.publicationTypes.keys())
        sortedKeys.sort(key = lambda item: len(  self.publicationTypes[item].assignmentRestriction ) )
        
        minimalRestrictions = len( self.publicationTypes[ sortedKeys[0] ].assignmentRestriction )
        
        queue = []
        
        for key in sortedKeys:
            if len(  self.publicationTypes[key].assignmentRestriction ) == minimalRestrictions:
                newPath = Path(self.publicationTypes)
                newPath.addItem(key, self.publicationTypes)
                queue.append( newPath )
            else:
                break
            
        print("in queue: ", len(queue))
        while len(queue[0].notAnalysedNodes) > 0:
            newQueue = {}
            
            for path in queue:
                promisingNodes = path.findPromisingNodes(self.publicationTypes)
                for node in promisingNodes:
                    newPath = deepcopy(path)
                    newPath.addItem(node, self.publicationTypes)
                    if newPath.maxInteractions > interactionLimit :
                        continue
                    
                    newKey = newPath.getKey()
                    if not newKey in newQueue:
                        newQueue[newKey] = newPath
                    elif newPath.maxInteractions < newQueue[newKey].maxInteractions:
                        newQueue[newKey] = newPath
                    else:
                        continue
                        
                    if len(queue) > 80:
                        break
                        
            queue = list(newQueue.values())
            print("in queue: ", len(queue))
        
        bestPath = None
        lowestInteractions = 10000
        lowestInteractionSum = -1
        
        for path in queue:
            if path.maxInteractions < lowestInteractions:
                lowestInteractions = path.maxInteractions
                lowestInteractionSum = path.interactionSum
                bestPath = path
                
            elif path.maxInteractions == lowestInteractions and path.interactionSum < lowestInteractionSum:
                lowestInteractionSum = path.interactionSum
                bestPath = path
                
        sortedPublications = []
        
        for key in bestPath.path:
            sortedPublications += self.publicationTypes[key].items
            
        return sortedPublications
            
        
        
        