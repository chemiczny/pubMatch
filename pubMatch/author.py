#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 18:26:38 2018

@author: michal
"""

class Author:
    def __init__ (self , name, slots, time, workerId):
        self.name = name
        self.names = [ n.strip() for n in name.split("-") ]
        self.slots = slots
        self.time = time
        self.id = workerId

