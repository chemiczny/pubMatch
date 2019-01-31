#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 13:03:51 2019

@author: michal
"""
import networkx as nx
import matplotlib.pyplot as plt

def plotGraph( mkarObject ):
    plt.figure()
    layout = nx.spring_layout(mkarObject.pubGraph)
    nx.draw_networkx(mkarObject.pubGraph, layout)