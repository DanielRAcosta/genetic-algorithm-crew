"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019

Classe População
"""

import variaveisGlobais as gl

import random as rd
import numpy as np


class Populacao:
    def __init__(self, npop, nome):       #única classe que pode ser inicializada vazia (sem soluções)
        self.sols = {}              #dicionario de soluções que compoem a populaçao
        self.npop = npop            #populaçao maxima escolhida
        self.nome = nome
    
    ### ADIÇÃO ######

    def addSol(self, solx): self.sols.update({solx.idsol : solx}) #adiciona uma solução a essa população0\

    def addSolCheck(self, solx):
        solx.sortV()
        custox = solx.custo()
        contemx = False 
        for soly in self.sols:
            self.sols[soly].sortV()
            if self.sols[soly].viagSol == solx.viagSol and self.sols[soly].custo() == custox: contemx = True
        
        if not contemx:
            self.addSol(solx)
            return True
        else: return False
        
    def excluiDet(self): #exclui deterministicamente as soluções com o maior custo
        qtde_solucoes_sobrando = len(self.sols)-self.npop #serão excluídas todas as soluções extras em relação à população máxima npop
        if qtde_solucoes_sobrando>0:
            nlist = list(self.sols) # lista dos indexes
            nlist.sort(key=lambda indexSol : self.sols[indexSol].custo()) #organiza indexes por ordem ascendente de custo
            solucoes_sobrando = nlist[-qtde_solucoes_sobrando:]
            for i in solucoes_sobrando: self.sols.pop(i) #exclui da população as referidas soluções
            
    def excluiRol(self): #serão excluídas todas as soluções extras em relação à população máxima npop
        if len(self.sols) > self.npop:
            roleta, erroRoleta = self.Roleta(self.npop,list(self.sols))
            solucoes_sobrando = [sol for sol in self.sols if sol not in roleta]
            for i in solucoes_sobrando: self.sols.pop(i)
        
    ### GENÉTICOS ######

    def Roleta(self, n, nlist):
        custos = [self.sols[sol].custo().total_seconds() for sol in self.sols] # custos das soluções
        maxc = max(custos)
        custos = [maxc-c for c in custos] #inverte e converte, o de maior custo é zero e o de menor custo é o maximo
        maxc = max(custos)
        custos = [c + maxc*gl.probMaiorCusto for c in custos] # adiciona um piso de probabilidade para o com maior custo não ser zero
        somac = sum(custos) 
        if somac > 0:
            custos = [c/somac for c in custos] # normalizados. agora podem ser usados como pesos
            nchoices = np.random.choice(nlist, size=n, replace=False, p=custos)
            return list(nchoices), False
        else:
            nchoices = np.random.choice(nlist, size=n, replace=False)
            #gl.logf.write("somac = 0 - Roleta com pesos iguais")
            gl.custosIguais = gl.custosIguais+1
            return list(nchoices), True # retorna que deu erro!
    
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
        nlist = [key for key in self.sols if self.sols not in duplicatas]
        return self.Roleta(n, nlist)
    
    def selecFinal(self): #talvez seja útil mas nessa etapa é bom um olhar humano
        if len(self.sols)>0:
            idSols = [idsol for idsol in self.sols if len(self.sols[idsol].viagSol) == len(gl.vdict['hi'])]
            idSols.sort(key=lambda idsol: self.sols[idsol].custo())
            return idSols[0]
        else: pass # o que fazer quando for uma população vazia pra nao estragar na hora de fazer a comparaçao?

    ### PRINTS ######
    
    def sizeViagSol(self):
        sizes = [len(self.sols[iSol].viagSol) for iSol in self.sols]
        return str(max(sizes))+"/"+str(min(sizes))
    
    def sizeServSol(self):
        sizes = [len(self.sols[iSol].servs) for iSol in self.sols]
        return str(max(sizes))+"/"+str(min(sizes))
    
    def gantt(self, outputPopFolder):
        for sol in self.sols: self.sols[sol].gantt(outputPopFolder, self.nome)
        
    def resta(self): return len(gl.vdict['hi']) - max([len(self.sols[iSol].viagSol) for iSol in self.sols])
    
    def resumo(self):
        resFile = open(gl.folder+'resumo_'+self.nome+'.txt','a')
        resFile.write('Resumo População '+self.nome+' / npop = '+str(self.npop)+'\nid, Iteração Origem, Quantidade de Serviços, Custo (s), Folgas Externas (s), Folgas Internas (s)')
        for i in self.sols:
            resFile.write('\n'+str(i)+','+str(self.sols[i].iAlgSol)+','+str(len(self.sols[i].servs))+','+str(self.sols[i].custo().total_seconds())+','+str(self.sols[i].folgaE().total_seconds())+','+str(self.sols[i].folgaI().total_seconds()))
        resFile.close()

# FUNÇÕES PICKLE - precisam agir fora da classe População
