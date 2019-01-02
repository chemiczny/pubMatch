#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 16:13:15 2019

@author: michal
"""

from IOtemp import readAuthors, readPublications
from publicationMatcher import PublicationMatcher
from math import ceil 

def checkN(workersList):
    N = 0
    for w in workersList:
        N += w.time
        
    return ceil(N/4.)*3

workersList = readAuthors("pracownicy.xls")
publicationsList = readPublications("publikacje.xls", workersList)

N = checkN(workersList)
pm = PublicationMatcher(workersList, publicationsList)

publicationsIds = pm.getAllPublicationsFromMainGraph()
data = pm.maxPointsFromFlowTheory(publicationsIds, N, True)

maxPoinst = data["maxPoints"]
maxSlots = data["maxSlots"]
flowG = data["flowGraph"]
flowDict = data["flowDict"]

def writeSlotsUsageLog( pubMatch, flowDict , logName ):
    authorsIds = pubMatch.authorsDict.keys()
    
    log = open(logName, "w")
    log.write("Author\tSlots available\tSlots used\tSlots used[%]\n")
    
    for a in authorsIds:
        if a in flowDict:
            slotsUsed = flowDict[a]["t"]/100.
        else:
            slotsUsed = 0
        slotsAvailable = pm.authorsDict[a].slots/100.
        if slotsAvailable > 0:
            log.write(a+"\t"+str(slotsAvailable)+"\t"+str(slotsUsed)+"\t"+str(slotsUsed*100/slotsAvailable)+"\n")
    
    
    log.close()

writeSlotsUsageLog( pm, flowDict, "slotsUsage.csv" )

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
            log.write(pObj.title.replace("\t", "") +"\t"+str(pObj.year)+"\t"+str(authors)+"\t"+str(pObj.points)+"\t"+str(pObj.size)+"\n")
    
    log.close()

writeUnusedPublicationsLog(pm, flowDict, "unusedPublications.csv")

def writeUsedPublicationsLog(pubMatch, flowDict, logName):
    pubIds = pubMatch.publicationDict.keys()
    
    log = open(logName, "w")
    log.write("Tytul\tRok\tAutorzy\tPunkty\Slots\n")
    
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
            authors = ", ".join(authors)
            log.write(pObj.title.replace("\t", "") +"\t"+str(pObj.year)+"\t"+str(authors)+"\t"+str(pObj.points)+"\t"+str(pObj.size)+"\n")
    
    log.close()

writeUsedPublicationsLog(pm, flowDict, "usedPublications.csv")
