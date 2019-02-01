#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 16:13:15 2019

@author: michal
"""

from IOtemp import readAuthors, readPublications
from MKAR_flow import MKAR_FlowTheory
from math import ceil 
import networkx as nx

def checkN(workersList):
    N = 0
    for w in workersList:
        N += w.time
        
    return ceil(N/4.)*3

#workersList = readAuthors("data/pracownicy.xls")
workersList = readAuthors("data/adamczykGroup.xls")
publicationsList = readPublications("data/publikacje.xls", workersList)
postFix = "All"

N = checkN(workersList)
pm = MKAR_FlowTheory(workersList, publicationsList)
pm.preprocessing()
publicationsIds = pm.getAllPublicationsFromMainGraph()
data = pm.solveFlowProblem(publicationsIds, N, True)

maxPoinst = data["maxPoints"]
maxSlots = data["maxSlots"]
flowG = data["flowGraph"]
flowDict = data["flowDict"]

print("Maksymalna liczba punktow: ", maxPoinst)
print("Maksymalna liczba wykorzystanych slotów: ", maxSlots)

uniqueWeights = set()
for p in pm.publicationList:
    uniqueWeights.add(  p.size)

def writeSlotsUsageLog( pubMatch, flowDict , logName ):
    authorsIds = pubMatch.authorsDict.keys()
    
    log = open(logName, "w")
    log.write("Author\tSlots available\tSlots used\tSlots used[%]\tall publication no\n")
    
    for a in authorsIds:
        if a in flowDict:
            slotsUsed = flowDict[a]["t"]/100.
            pubNo = len(list(pubMatch.pubGraph.neighbors(a)))
        else:
            slotsUsed = 0
            pubNo = 0
            
        slotsAvailable = pm.authorsDict[a].slots/100.
        
        if slotsAvailable > 0:
            log.write(a+"\t"+str(slotsAvailable)+"\t"+str(slotsUsed)+"\t"+str(slotsUsed*100/slotsAvailable)+"\t"+str(pubNo)+"\n")
    
    
    log.close()

writeSlotsUsageLog( pm, flowDict, "slotsUsage"+postFix+".csv" )

def writeUnusedPublicationsLog(pubMatch, flowDict, logName):
    pubIds = pubMatch.publicationDict.keys()
    
    log = open(logName, "w")
    log.write("Tytul\tRok\tAutorzy\tPunkty\tSlots available\n")
    
    for p in pubIds:
        if p in flowDict:
            slotsUsed = 0
            for c in flowDict[p]:
                slotsUsed += flowDict[p][c]
        else:
            slotsUsed = 0
        
        pObj = pm.publicationDict[p]
        
        if slotsUsed == 0:
            authors = [ a.name for a in pObj.authors ]
            authors = ", ".join(authors)
            log.write(pObj.title.replace("\t", "") +"\t"+str(pObj.year)+"\t"+str(authors)+"\t"+str(pObj.points/100.)+"\t"+str(pObj.size/100.)+"\n")
    
    log.close()

writeUnusedPublicationsLog(pm, flowDict, "unusedPublications"+postFix+".csv")

def writeUsedPublicationsLog(pubMatch, flowDict, logName):
    pubIds = pubMatch.publicationDict.keys()
    
    log = open(logName, "w")
    log.write("Tytul\tRok\tAutorzy\tPunkty\tSlots\tFractional\n")
    
    for p in pubIds:
        authors = []
        if p in flowDict:
            slotsUsed = 0
            for c in flowDict[p]:
                slotsUsed += flowDict[p][c]
                if flowDict[p][c] > 0:
                    authors.append(c+ "("+str(flowDict[p][c])+")")
        else:
            slotsUsed = 0
        
        pObj = pm.publicationDict[p]
        
        if slotsUsed > 0:
            authorsNo = len(authors)
            fractional = False
            if authorsNo > 1 or slotsUsed < pObj.size:
                fractional = True
            
            authors = ", ".join(authors)
            log.write(pObj.title.replace("\t", "") +"\t"+str(pObj.year)+"\t"+str(authors)+"\t"+str(pObj.points/100.)+"\t"+str(pObj.size/100.)+"\t"+str(fractional)+"\n")
    
    log.close()

writeUsedPublicationsLog(pm, flowDict, "usedPublications"+postFix+".csv")
fractional = pm.extractFractionalGraph(flowDict)
pm.pubGraph = fractional
pm.printStatus()
layout = nx.spring_layout(fractional)
nx.draw_networkx(fractional, layout)
