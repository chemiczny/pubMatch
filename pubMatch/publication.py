#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 18:26:46 2018

@author: michal
"""

class Publication:
    def __init__(self, authors, points, size,  title, year, publicationAuthorId, pubId):
        self.authors = authors
        self.points = points
        self.size = size
        self.title = title
        self.year = year
        self.id = publicationAuthorId
        self.uniqueId = pubId

