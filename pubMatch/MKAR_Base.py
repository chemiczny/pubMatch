#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 12:46:05 2019

@author: michal
"""
import networkx as nx

class MKAR:
    def __init__ (self,  authorsList, publicationList ):
        self.authorsList = authorsList
        self.publicationList = publicationList
        
        self.publicationDict = pubsList2dict(publicationList)
        self.authorsDict = authorsList2dict(authorsList)
        
        self.components = []
        self.generatePublicationGraph()
        
        self.removedPublications = []
        
        statusFile = open("status.log", 'w')
        statusFile.close()
        
    def copyFromMKAR(self, mkar):
        self.authorsList = mkar.authorsList
        self.publicationList = mkar.publicationList
        
        self.publicationDict = mkar.publicationDict
        self.authorsDict = mkar.authorsDict
        
        self.components = mkar.components
        self.pubGraph = mkar.pubGraph
        
        self.removedPublications = mkar.removedPublications
        
    
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


    def divideGraph(self):
        self.components = list(nx.connected_component_subgraphs(self.pubGraph))
                
    
    def countPublicationsInMainGraph(self):
        return len(self.getAllPublicationsFromMainGraph())
    
    def getAllPublicationsFromMainGraph(self):
        pubs = []
        for node in self.pubGraph.nodes:
            if self.pubGraph.nodes[node]["type"] == "publication":
                pubs.append(node)
                
        return pubs
    
    def removeIsolatedNodes(self):
        print("################################")
        print("Searching for isolated nodes")
        
        isolated = list(nx.isolates(self.pubGraph))
        
        print("Found ", len(isolated))
        self.pubGraph.remove_nodes_from(isolated)
        
    def mergeSubgraphs(self):
        for subg in self.subGraphs:
            self.pubGraph = nx.compose(self.pubGraph, subg)
            
        self.subGrahs = []
    
    def printStatus(self):
        print("################################")
        print("Graph Status")
        print("Nodes: ", len(self.pubGraph.nodes))
        print("Edges: ", len(self.pubGraph.edges))
        pubLen = len(self.getAllPublicationsFromMainGraph())
        print("Authors: ", len(self.pubGraph.nodes) - pubLen )
        print("Publications: ", pubLen)
        
        self.divideGraph()
        print("Inedepndent components: ",len(self.components))
        compLen = [ len(c.nodes()) for c in self.components ]
        print(compLen)
        
        statusFile = open("status.log", 'a')
        statusFile.write("################################\n")
        statusFile.write("Graph Status\n")
        statusFile.write("Nodes: " + str( len(self.pubGraph.nodes))+"\n")
        statusFile.write("Edges: " + str(len(self.pubGraph.edges))+"\n")
        statusFile.write("Authors: " + str(len(self.pubGraph.nodes) - pubLen)+"\n" )
        statusFile.write("Publications: " + str( pubLen)+"\n" )
        
        statusFile.write("Inedepndent components: " + str(len(self.components)) +"\n")
        statusFile.write(str(compLen)+"\n")
        
        statusFile.close()
    
    def preprocessing(self):
        self.printStatus()
        self.removeUnnecessaryPublications()
        self.removeUnnecessaryEdges()
        self.removeIsolatedNodes()
        self.printStatus()
        
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
    
    def removeUnnecessaryPublications(self):
        """Jesli autor ma kilka publikacji o identycznej masie, ktorych laczna masa przekracza jego ilosc slotow to zostaw najcenniejsze """
        print("################################")
        print("Searching for publications to remove")
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
                    print("Found author with publications to remove: ", author)
                    print("Remove ",  n, " from " ,pubsNo, " publications with weight ", weight )
                    print("Available slots: ",  self.authorsDict[author].slots)
                    
                    interestingPubs = [ self.publicationDict[pubId] for pubId in weight2pubs[weight] ]
                    interestingPubs = sorted( interestingPubs, key=lambda x: x.points)
                    
                    pointReference = interestingPubs[n+1].points
#                    print("najgorsza z najlepszych", pointReference)
                    
                    print([ip.points for ip in interestingPubs])
                    interestingPubs = interestingPubs[ : int(n) ]
                    
                    for ip in interestingPubs:
                        print("Removing: ", ip.points , "points")
                        self.pubGraph.remove_node(ip.id)
                        self.removedPublications.append(ip)
                        
                    
                    otherPubs = self.pubGraph.neighbors( author )
                    otherPubs = set(otherPubs) - set(pubs)
                    
                    for op in otherPubs :
                        if self.publicationDict[ op].size == weight and self.publicationDict[ op].points <= pointReference:
#                            print("usuwam krawedz",self.publicationDict[ op].size, self.publicationDict[ op].points )
                            self.pubGraph.remove_edge(author, op)
                            
    def removeUnnecessaryEdges(self ):
        print("################################")
        print("Searching for connections to remove")
        somethingWasFound = True
        
        separatedGraphs = []
        while somethingWasFound:
            somethingWasFound = False
            
            for author in self.authorsList:
                name = author.name
                if name in self.pubGraph.nodes:
                    pubs = list(self.pubGraph.neighbors(name))
                    sumWeight = self.getWeightSum(pubs)
                    if sumWeight <= author.slots:
                        separatedGraphs.append( nx.Graph( self.pubGraph.subgraph( pubs + [ name ] ) ) )
                        self.pubGraph.remove_nodes_from( pubs + [ name ]  )
#                        self.pubGraph = nx.compose(self.pubGraph, separatedGraph)
                        print("Separating author: ", name)
                        print("publications weight: ", sumWeight)
                        print("available slots" , author.slots)
                        somethingWasFound = True
    
        for sp in separatedGraphs:
            self.pubGraph = nx.compose(self.pubGraph, sp)
            
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