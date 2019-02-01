#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 16:41:48 2018

@author: michal
"""

class Solution:
    def __init__(self):
        self.publication2authors = {}
        self.authors2usedSlots = {}
        self.actualWeight = 0
        self.actualPoints = 0
        self.boundary = 0
        
    def addConnection(self, author, publication):
        authorName = author.name
        
        usedSlots = 0
        if authorName in self.authors2usedSlots:
            usedSlots = self.authors2usedSlots[authorName]
            
        if usedSlots + publication.size > author.slots:
            return False
        
        if not authorName in self.authors2usedSlots:
            self.authors2usedSlots[authorName] = 0
            
        self.publication2authors[publication.id] = authorName
        self.authors2usedSlots[authorName] += publication.size
        
        self.actualWeight += publication.size
        self.actualPoints += publication.points
        
        return True
        