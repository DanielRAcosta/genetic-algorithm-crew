# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 09:12:44 2019

@author: Daniel
"""
import pickle as pk 

pkfile = open('C:\\Users\\Daniel\\Google Drive\\TCC Daniel Acosta\\GitHub\\genetic-algorithm-crew\\Programa\\output\\24\\pop_f.txt', mode='br')
pop24 = pk.load(pkfile)
pkfile.close()

pkfile2 = open('C:\\Users\\Daniel\\Google Drive\\TCC Daniel Acosta\\GitHub\\genetic-algorithm-crew\\Programa\\output\\25\\pop_f.txt', mode='br')
pop25 = pk.load(pkfile2)
pkfile2.close()