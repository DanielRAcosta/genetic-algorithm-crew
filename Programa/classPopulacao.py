#%%
"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""

import variaveisGlobais as gl
import random as rd
import numpy as np
import datetime as dtm
import pickle as pk
#import os

def outpop(pop, nome):
    nomefile = gl.folder+'output\\pop_'+nome+'.txt'
    #os.remove(nomefile)
    pkfile = open(nomefile, mode='bw')
    pk.dump(pop,pkfile)
    pkfile.close()
    
def inpop(nome):
    pkfile = open(gl.folder+'output\\pop_'+nome+'.txt', mode='br')
    return pk.load(pkfile)
    pkfile.close()

class Populacao:                    #decidir como lidar com a população - como lidar com o tamanho fixo?
    def __init__(self, npop):       #única classe que pode ser inicializada vazia (sem soluções)
        self.sols = {}              #dicionario de soluções que compoem a populaçao
        self.npop = npop            #populaçao maxima escolhida

    ### ADIÇÃO ################

    def addSol(self, solx): self.sols.update({solx.idsol : solx}) #adiciona uma solução a essa população0\
        
    def excluiDet(self): #exclui deterministicamente as soluções com o maior custo
        qtde_solucoes_sobrando = len(self.sols)-self.npop #serão excluídas todas as soluções extras em relação à população máxima npop
        if qtde_solucoes_sobrando>0:
            nlist = list(self.sols) # lista dos indexes
            nlist.sort(key=lambda indexSol : self.sols[indexSol].custo()) #organiza indexes por ordem ascendente de custo
            solucoes_sobrando = nlist[-qtde_solucoes_sobrando:]
            for i in solucoes_sobrando: self.sols.pop(i) #exclui da população as referidas soluções
        
    ### GENÉTICOS - seleção ###################

    def selecDet(self, n, idsols): #seleciona deterministicamente as n soluções com menor custo
        #duplicatas = [key for key in self.sols if self.sols[key].idsol in idsols]
        nlist = [key for key in self.sols] #if self.sols not in duplicatas]
        nlist.sort(key=lambda indexSol : self.sols[indexSol].custo()) # ordena por custo (ascendente)
        return nlist[:n] # retorna apenas os n primeiros da lista
    
    def selecRand(self, n, idsols): #seleciona soluções aleatoriamente
        duplicatas = [key for key in self.sols if self.sols[key].idsol in idsols]
        nlist = [key for key in self.sols if self.sols not in duplicatas]
        rd.shuffle(nlist) #aleatoriza os indices
        return nlist[:n] # retorna apenas os n primeiros da lista
    
    def selecRoleta(self, n, idsols):
        duplicatas = [key for key in self.sols if self.sols[key].idsol in idsols]
        #print("duplicatas", duplicatas)
        nlist = [key for key in self.sols if self.sols not in duplicatas]
        #print("nlist", nlist)
        
        custos = [self.sols[sol].custo() for sol in self.sols] # custos das soluções
        maxc = max(custos)
        #print("maxc",maxc)
        custos = [dtm.timedelta.total_seconds(maxc-c) for c in custos] #inverte e converte, o de maior custo é zero e o de menor custo é o maximo
        #print("custos sec invert", custos)
        maxc = max(custos)
        custos = [c + maxc*gl.probabMaiorCusto for c in custos] # adiciona um piso de probabilidade para o com maior custo não ser zero
        #print("custos + 0.05*maxcustos", custos)
        somac = sum(custos) 
        print("soma2", somac)
        if somac > 0:
            custos = [c/somac for c in custos] # normalizados. agora podem ser usados como pesos
            print("custos pesos", custos)        
            nchoices = np.random.choice(nlist, size=n, replace=False, p=custos)
            print("retorna", nchoices)
            return nchoices
        else:
            nchoices = np.random.choice(nlist, size=n, replace=False)
            gl.custosIguais = gl.custosIguais+1
            return nchoices

    ### PRINTS ##################################
    
    def prpop(self): # print útil
        print("")
        print("FUNÇÃO PRINT POPULAÇÃO")
        print("")
                
        for i in self.sols:
            print ("Solução numero", i, "--------------------------------")
            self.sols[i].prsol()
            print ("Custo = ", self.sols[i].custo())
    
    def maxViagSol(self):
        return max([len(self.sols[iSol].viagSol) for iSol in self.sols])
    
    def prSolCost(self):
        for iSol in self.sols: print(iSol, " - custo ", self.sols[iSol].custo())
