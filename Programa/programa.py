"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""

import variaveisGlobais as gl
import classServico as sv
import classSolucao as sl
import classPopulacao as pp

import plotly.express as px
import random as rd
import numpy as np
import pandas as pd
import math
import datetime
import os
    
def plot_conv():
    fileConv= open(gl.folder+ "output\\"+gl.outputPopFolder+"\\convergencia.txt")
    dfconv = pd.read_csv(fileConv, sep=',')
    xplot = list(dfconv['iAlg']) + list(dfconv['iAlg']) + list(dfconv['iAlg'])
    yplot = list(dfconv['custo'])+ list(dfconv['custoG'])+list(dfconv['custoH'])
    figconv = px.scatter(x=xplot, y=yplot)
    figconv.show()
    
def guardaExecucao(popA,popB,popC, outputPopFolder):
    pp.outpop(popA, 'a', outputPopFolder)    
    pp.outpop(popB, 'b', outputPopFolder)    
    pp.outpop(popC, 'c', outputPopFolder)    , outputPopFolder, outputPopFolder
    pp.outpop(gl.popCompl, 'f', outputPopFolder)
    pp.outpop(gl.popQuase, 'q', outputPopFolder)
    pp.outpop(gl.idsolGlob, 'id', outputPopFolder)
    
def outConv(fileConv, sol, iAlg):
    # convergencia.txt
    conv = open(fileConv, 'a')
    conv.write('\n'+str(iAlg)+','+str(sol.idsol)+','+str(len(sol.viagSol))+','+str(len(sol.servs))+','+str(sol.custo().total_seconds())+','+str(sol.custog().total_seconds())+','+str(sol.custoh().total_seconds()))
    conv.close()

def principal(iAlg,popA,popB,popC, outputPopFolder):
    popC.sols.clear() #esvazia B para recomeçar
    
    ### CRUZAMENTO ############
    # pra cada um dos nb melhores integrantes de A, de acordo com a função seleçãoDeterminística 
    
    pais1 = popA.selecDet(round(gl.fs*gl.na),[]) # seleciona os pais de A que servem como base
    
    selecE = {} # lista de pais de E - criada fora pra que não haja duplicatas
    for iSol in pais1:
        vx = popA.sols[iSol].viagNovaRandom()
        while vx in selecE: vx = popA.sols[iSol].viagNovaRandom()
        selecE.update({iSol: vx})
    
    for iSol in pais1:  # CRUZAMENTO popB->popC - os pais dos cruzamentos aqui são buscados diretamente em popA
        
        for jSol in range(gl.nCruz): # cruza com E (vdict) um nCruz numero de vezes
            vx = selecE[iSol]
            if vx is not False: 
                ex = sl.Solucao(sv.Servico(vx), [0,0]) # cria solução com viagem que ainda não existe em popB
                filho, alterou = popA.sols[iSol].cruza(ex) #filho CE
                if alterou: popC.addSol(filho)            
                filho, alterou = ex.cruza(popA.sols[iSol]) #filho EC
                if alterou: popC.addSolCheck(filho)
            
        for jSol in popA.selecRoleta(gl.nCruz,pais1)[0]: #cruza com popA um nCruz numero de vezes, envia ids dos pais para não haver duplicatas
            filho, alterou = popA.sols[iSol].cruza(popA.sols[jSol]) #filho CA
            if alterou: popC.addSolCheck(filho)                
            filho, alterou = popA.sols[jSol].cruza(popA.sols[iSol]) #filho AC
            if alterou: popC.addSolCheck(filho)
        
        if iAlg+gl.modo_inicio>1: # cruza com popB - apenas se popB já existe
            for jSol in popB.selecRoleta(gl.nCruz,[])[0]:  #cruza com popB até um nCruz numero de vezes               
                filho, alterou = popA.sols[iSol].cruza(popB.sols[jSol]) #filho CB
                if alterou: popC.addSolCheck(filho)
                filho, alterou = popB.sols[jSol].cruza(popA.sols[iSol]) #filho BC
                if alterou: popC.addSolCheck(filho)
            
        if gl.carregaPais == 1: # se os pais devem permanecer para poderem ser selecionados
            popC.addSolCheck(popA.sols[iSol])
            #só no final os pais advindos de A são adicionados à população, para que também sejam passíveis de mutação na próxima etapa
        if gl.carregaPais == 0 and popC.sols == {}: # se os pais devem permanecer para poderem ser selecionados
            #caso especial: se eu impedi os pais de serem levados adiante e se não consegui criar nenhum filho novo
            #C está vazio, então vou sortear um de A para ir e mutar
            popC.addSolCheck(popA.sols[iSol])
            choice = np.random.choice(list(popC.sols), size=1, replace=False)[0]
            popC.sols[choice].muta()
        
    # EXCLUI deterministicamente/roleta as piores dos grupos constantes popA, popB e popCompletas
    popA.excluiRol()
    popB.excluiRol()
    gl.popCompl.excluiRol()
    
    ### MUTAÇÃO ############    
    for iSol in popC.sols: # mutação in-place
        if rd.random() < gl.pm:
            popC.sols[iSol].muta()
            print("muta ",iSol)
    
    ### SELEÇÃO ############
    
    # deterministica popC --> popB
    idsolsB = [popB.sols[key].idsol for key in popB.sols] # lista de idsols das soluções que existem em popB. deve entrar como argumento na função abaixo para evitar duplicatas
    melhores = popC.selecDet(math.ceil(gl.fatorTop*len(popC.sols)),idsolsB) # retorna iterador com as chaves das soluções escolhidas de popC
    for iSol in melhores: popB.addSolCheck(popC.sols[iSol]) # adiciona à população B as soluções escolhidas acima
    
    # roleta popC --> popA
    idsolsA = [popA.sols[key].idsol for key in popA.sols] # lista de idsols das soluções que existem em A. deve entrar como argumento na função abaixo para evitar duplicatas
    roleta, erroRoleta = popC.selecRoleta(math.floor(gl.fatorRol*len(popC.sols)),idsolsA) # retorna iterador com as keys das soluções escolhidas em B
    for iSol in roleta: popA.addSolCheck(popC.sols[iSol]) # adiciona à população A as soluções escolhidas acima
    
    ### SAÍDA DE DADOS #####

    print(iAlg, popA.sizeViagSol(), popB.sizeViagSol(), popC.sizeViagSol()) # plota na tela o número máximo de viagens
         
    if float(iAlg/30).is_integer(): # a cada 30 iterações
        gl.popQuase.excluiDet()
        if gl.modo_salva == 1: guardaExecucao(popA,popB,popC, outputPopFolder)
        
    if max(max(popA.sizeViagSol()),max(popB.sizeViagSol()),max(popC.sizeViagSol())) == len(gl.vdict['hi']):
        gl.gotCompl = gl.gotCompl + 1
        
    return popA,popB,popC
       
#### EXECUÇÃO DO ALGORITMO ####

def prog(iExec):
    
    outputPopFolder = str(iExec)
    if not os.path.exists(gl.folder + "output\\"+outputPopFolder +"\\"): os.mkdir(gl.folder + "output\\"+outputPopFolder +"\\")
    if not os.path.exists(gl.folder+"output\\"+str(outputPopFolder)+"\\gantt\\"): os.mkdir(gl.folder+"output\\"+str(outputPopFolder)+"\\gantt\\")
    fileConv = gl.folder+ "output\\"+outputPopFolder+"\\convergencia.txt"
    fileAtrib = gl.folder+ "output\\"+outputPopFolder+"\\atributos.txt"
    if os.path.exists(fileConv): os.remove(fileConv) # não deixar que o txt da convergencia seja reescrito
    if os.path.exists(fileAtrib): os.remove(fileAtrib) # não deixar que o txt da convergencia seja reescrito
    
    # Inicialização
    algStart = datetime.datetime.now()
    
    # inicializa plot convergência
    conv = open(fileConv, 'w')
    conv.write("\niAlg,idSol mais barata,nViagens,nServs,custo,custoG,custoH")
    conv.close()
    
    # inicializa arquivo atributos
    atrib = open(fileAtrib, 'w')
    atrib.write(str(algStart))
    atrib.close()
                      
    if gl.modo_inicio == 0:
        popA = pp.Populacao(gl.na, 'A')
        popB = pp.Populacao(gl.nb, 'B')
        popC = pp.Populacao(gl.nc, 'C')
        
        randlist = [] 
        for i in range(gl.na): # CRIA grupo de soluções iniciais A a partir de E - input = leitura de vdict, n populacao A (gl.na)
            vx = rd.randrange(1,len(gl.vdict['hi'])+1)
            while vx in randlist: vx = rd.randrange(1,len(gl.vdict['hi'])+1)
            randlist.append(vx)
            
        for vx in randlist: popA.addSol(sl.Solucao(sv.Servico(vx), [0,0]))
            
    elif gl.modo_inicio == 1:
        popA = pp.inpop('A')
        popB = pp.inpop('B')
        popC = pp.Populacao(gl.nc, 'C')  
    
    
    ### EXECUTA LAÇO PRINCIPAL ###
    if gl.modo_fim == 0: # modo 0 - executa um numero finito de iterações
        for iAlg in range(1,gl.alg+1):
            popA,popB,popC = principal(iAlg,popA,popB,popC, outputPopFolder)
            outConv(fileConv,popB.sols[popB.selecDet(1,[])[0]], iAlg)
            
    elif gl.modo_fim ==1: #modo 1 - itera até atingir um certo numero de soluções completas
        iAlg = 0  
        gl.solCompl = 0
        while gl.solCompl < gl.nCompl:
            iAlg = iAlg +1
            popA,popB,popC = principal(iAlg,popA,popB,popC, outputPopFolder)
            outConv(fileConv,popB.sols[popB.selecDet(1,[])[0]], iAlg)
    elif gl.modo_fim ==2:
        iAlg = 0  
        gl.solCompl = 0
        gl.gotCompl = 0
        while gl.gotCompl < gl.tryCompl:
            iAlg = iAlg +1
            popA,popB,popC = principal(iAlg,popA,popB,popC, outputPopFolder)
            outConv(fileConv,popB.sols[popB.selecDet(1,[])[0]], iAlg)
            
    # Finalização
    # guarda as populações num arquivo pickle para usar depois
    if gl.modo_salva == 1: guardaExecucao(popA,popB,popC, outputPopFolder)
    # anota atributos restantes
    algEnd = datetime.datetime.now()
    atrib = open(fileAtrib, 'w')
    atrib.write(str(gl.gotCompl)+str(iAlg)+str(algEnd)+str(algEnd-algStart))
    #escrever ate qual iteração foi
    atrib.close()
    
    # plotar todos os gantts
    popA.gantt(outputPopFolder)
    popB.gantt(outputPopFolder)
    popC.gantt(outputPopFolder)
    if len(gl.popCompl.sols)>0 :gl.popCompl.gantt(outputPopFolder)
    if len(gl.popQuase.sols)>0 :gl.popQuase.gantt(outputPopFolder)
    
    # plotar melhor gantt dessa execução
    # ainda não é bom sem a supervisao humana
    #idBest = [popA.selecFinal(), popA.selecFinal(),popA.selecFinal(),popA.selecFinal(),popA.selecFinal()]

    