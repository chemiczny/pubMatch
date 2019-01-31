#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 13:01:57 2019

@author: michal
"""

import sys
if not "../" in sys.path:
    sys.path.append('../')
    
from IOtemp import readAuthors, readPublications
from MKAR_flow import MKAR_FlowTheory
from plotGraph import plotGraph
    
workersList = readAuthors("../data/adamczykGroup.xls")
publicationsList = readPublications("../data/publikacje.xls", workersList)

mkar = MKAR_FlowTheory(workersList, publicationsList)
plotGraph(mkar)

mkar.preprocessing()

plotGraph(mkar)