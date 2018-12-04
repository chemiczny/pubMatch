#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 15:04:23 2018

@author: michal
"""
import pandas as pd
from math import isnan
from publication import Publication
from author import Author

def readPublications(excelFile, authors):
    publicationsSheet = pd.read_excel(excelFile)
    publicationsList = []
    notFoundAuthors = set()
    publicationsNotSet = []
    for i in publicationsSheet.index:
        title = publicationsSheet["Tytuł artykułu"][i]
        year = publicationsSheet["Data publikacji"][i]
        size = publicationsSheet["UDZIAŁ"][i]
        points = publicationsSheet["PUNKTACJA"][i]
        
        names = publicationsSheet["Autorzy"][i].upper()
        names = names.split(",")
        names = [ n.split()[-1].strip() for n in names ]
        
        authorsList = []
        
        for name in names:
            found = False
            for author in authors:
                if name == author.name:
                    if author.slots > 0:
                        authorsList.append(author)
                    found = True
                    break
                elif name == author.names[0] :
                    if author.slots > 0:
                        authorsList.append(author)
                    found = True
                    print("Utozsamiam ", name," z ", author.name)
                    break
            if not found:
#                print("Cannot find :", name)
                notFoundAuthors.add(name)
                
        if authorsList:
            publicationsList.append(  Publication(authorsList, int(round(points*100)), int(round(size*100)), title, year, i) )
        else:
            publicationsNotSet.append( [ names, title, year ])
                
    print("Nie znaleziono autorow: ", notFoundAuthors)
    print("Publikacje nie brane pod uwage:")
    for p in publicationsNotSet:
        print(p[0], p[1], p[2])
    return publicationsList

def readAuthors(excelFile):
    workersSheet = pd.read_excel(excelFile)
    workersList = []
    for i in workersSheet.index:
        name = workersSheet["Pracownik"][i].strip().upper()
        
        timeSum = 0
        for year in [  2014, 2015, 2016, 2017 ]:
            newTime = workersSheet[year][i]
            if isnan(newTime):
                newTime = 0
            timeSum += newTime
            
#        if timeSum > 0:
        workersList.append(Author(name, int(round(timeSum*100)), timeSum, i ))
            
    return workersList