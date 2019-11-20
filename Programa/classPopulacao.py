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

def inpop(nome):
    pkfile = open(gl.folder+'output\\'+gl.inputPopFolder+'\\pop_'+nome+'.txt', mode='br')
    return pk.load(pkfile)
    pkfile.close()
    
def outpop(pop, nome):
    pasta = gl.folder+'output\\'+gl.outputPopFolder
    if not os.path.exists(pasta): os.mkdir(pasta)
    nomefile = pasta+'\\pop_'+nome+'.txt'
    if os.path.exists(nomefile): os.remove(nomefile)
    pkfile = open(nomefile, mode='bw')
    pk.dump(pop,pkfile)
    pkfile.close()

class Populacao:                    #decidir como lidar com a população - como lidar com o tamanho fixo?
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
            
        if contemx:
            gl.logf.write("\n[addSolCheck - pop "+str(len(self.sols))+"] Filho não adicionado à população.")
        else:
            self.addSol(solx) #filho EC
            gl.logf.write("\n[addSolCheck - pop "+str(len(self.sols))+"] Filho adicionado à população.")
        
    def excluiDet(self): #exclui deterministicamente as soluções com o maior custo
        qtde_solucoes_sobrando = len(self.sols)-self.npop #serão excluídas todas as soluções extras em relação à população máxima npop
        if qtde_solucoes_sobrando>0:
            nlist = list(self.sols) # lista dos indexes
            nlist.sort(key=lambda indexSol : self.sols[indexSol].custo()) #organiza indexes por ordem ascendente de custo
            solucoes_sobrando = nlist[-qtde_solucoes_sobrando:]
            for i in solucoes_sobrando: self.sols.pop(i) #exclui da população as referidas soluções
            
    def excluiRol(self): #serão excluídas todas as soluções extras em relação à população máxima npop
        if len(self.sols) > self.npop:
            #gl.wrRoleta = open(gl.folder+"output\\wrRoletaCA.txt",'a')
            roleta, erroRoleta = self.Roleta(self.npop,list(self.sols))
            solucoes_sobrando = [sol for sol in self.sols if sol not in roleta]
            for i in solucoes_sobrando: self.sols.pop(i)
        
    ### GENÉTICOS - seleção ######

    def Roleta(self, n, nlist):
        custos = [self.sols[sol].custo().total_seconds() for sol in self.sols] # custos das soluções
        #gl.wrRoleta.write(str(custos)+',')
        maxc = max(custos)
        #gl.wrRoleta.write(str(maxc)+',')
        custos = [maxc-c for c in custos] #inverte e converte, o de maior custo é zero e o de menor custo é o maximo
        #gl.wrRoleta.write(str(custos)+',')
        maxc = max(custos)
        #gl.wrRoleta.write(str(maxc)+',')
        custos = [c + maxc*gl.probMaiorCusto for c in custos] # adiciona um piso de probabilidade para o com maior custo não ser zero
        #gl.wrRoleta.write(str(custos)+',')
        somac = sum(custos) 
        #gl.wrRoleta.write(str(somac)+',')
        if somac > 0:
            custos = [c/somac for c in custos] # normalizados. agora podem ser usados como pesos
            #gl.wrRoleta.write(str(custos)+',')
            #print(max(custos), "dif?", min(custos))        
            nchoices = np.random.choice(nlist, size=n, replace=False, p=custos)
            #gl.wrRoleta.write(str(list(nchoices))+',')
            return list(nchoices), False
            #gl.wrRoleta.close()
        else:
            nchoices = np.random.choice(nlist, size=n, replace=False)
            gl.logf.write("somac = 0 - Roleta com pesos iguais")
            #gl.wrRoleta.write("somac = 0 - Roleta com pesos iguais")
            gl.custosIguais = gl.custosIguais+1
            #gl.wrRoleta.close()
            return list(nchoices), True
    
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
        #gl.wrRoleta = open(gl.folder+"output\\wrRoletaCA.txt",'a')
        duplicatas = [key for key in self.sols if self.sols[key].idsol in idsols]
        #gl.wrRoleta.write(str(duplicatas)+',')
        nlist = [key for key in self.sols if self.sols not in duplicatas]
        #gl.wrRoleta.write(str(nlist)+',')
        return self.Roleta(n, nlist)

    ### PRINTS ######
    
    def prpop(self): # print útil
        print("")
        print("FUNÇÃO PRINT POPULAÇÃO")
        print("")
                
        for i in self.sols:
            print ("Solução numero", i, "--------------------------------")
            self.sols[i].prsol()
            print ("Custo = ", self.sols[i].custo())
    
    def sizeViagSol(self): return [len(self.sols[iSol].viagSol) for iSol in self.sols]
    
    def sizeServSol(self): return [len(self.sols[iSol].servs) for iSol in self.sols]
    
    def prSolCost(self):
        for iSol in self.sols: print(iSol,',', self.sols[iSol].custo(), ',')
        
    def wrpop(self, iAlg):
        pop = open(gl.folder + "output\\wrpop"+self.nome+".txt", 'a')
        pop.write("\n[POP"+self.nome+"] iAlg, sol, idSol, custoG [segundos], custoH [segundos], qtde Servs, qtde Viags, viags ")    
        for sol in self.sols:
            out = '\n' + str(iAlg) + ',' + str(sol) + ',' + str(self.sols[sol].idsol) + ',' + str(self.sols[sol].custog().total_seconds()) + ',' + str(self.sols[sol].custoh().total_seconds()) + ',' + str(len(self.sols[sol].servs)) + ',' + str(len(self.sols[sol].viagSol)) + ',' + str(self.sols[sol].viagSol)
            pop.write(out)
        pop.close()

    def gantt(self, iAlg):
        for sol in self.sols: self.sols[sol].gantt(iAlg, self.nome)
    
