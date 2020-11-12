"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019

Algoritmo Principal
"""

import variaveisGlobais as gl
import classServico as sv
import classSolucao as sl
import classPopulacao as pp
import plot

import random as rd
import numpy as np
import math
import datetime
import os
       
def guardaExecucao(popA,popB,popC, outputPopFolder):
    gl.outpop(popA, 'a', outputPopFolder)    
    gl.outpop(popB, 'b', outputPopFolder)    
    gl.outpop(popC, 'c', outputPopFolder)
    gl.outpop(gl.popCompl, 'f', outputPopFolder)
    gl.outpop(gl.popCompl, 'f', 'base')
    #gl.outpop(gl.popQuase, 'q', outputPopFolder)
    gl.outpop(gl.idsolGlob, 'id', outputPopFolder)
    # guardar iAlg tbm

#### Laço Iterativo Principal a ser chamado no Algoritmo abaixo
def principal(popA,popB,popC, outputPopFolder):
    popC.sols.clear() #esvazia B para recomeçar
    
    #### CRUZAMENTO ############
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
        
        if gl.igl+gl.modo_inicio>1: # cruza com popB - apenas se popB já existe
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
    #gl.popQuase.excluiRol()
    
    ### MUTAÇÃO ############    
    for iSol in popC.sols: # mutação in-place
        if rd.random() < gl.pm:
            popC.sols[iSol].muta()
            #print("muta ",iSol)
    
    
    ### SELEÇÃO ############
    
    # deterministica popC --> popB
    idsolsB = [popB.sols[key].idsol for key in popB.sols] # lista de idsols das soluções que existem em popB. deve entrar como argumento na função abaixo para evitar duplicatas
    melhores = popC.selecDet(math.ceil(gl.fatorTop*len(popC.sols)),idsolsB) # retorna iterador com as chaves das soluções escolhidas de popC
    for iSol in melhores: popB.addSolCheck(popC.sols[iSol]) # adiciona à população B as soluções escolhidas acima
    
    # roleta popC --> popA
    idsolsA = [popA.sols[key].idsol for key in popA.sols] # lista de idsols das soluções que existem em A. deve entrar como argumento na função abaixo para evitar duplicatas
    roleta, erroRoleta = popC.selecRoleta(math.floor(gl.fatorRol*len(popC.sols)),idsolsA) # retorna iterador com as keys das soluções escolhidas em B
    for iSol in roleta: popA.addSolCheck(popC.sols[iSol]) # adiciona à população A as soluções escolhidas acima
         
    if float(gl.igl/30).is_integer(): # a cada 30 iterações
        #gl.popQuase.excluiDet()
        if gl.modo_salva == 1: guardaExecucao(popA,popB,popC, outputPopFolder)
        
    if max(max(popA.sizeViagSol()),max(popB.sizeViagSol()),max(popC.sizeViagSol())) == len(gl.vdict['hi']):
        gl.gotCompl = gl.gotCompl + 1 #se tem alguma solução em alguma pop que tem todas as viagens da TH, registra aqui uma vez por iteração
        
    return popA,popB,popC
       
#### Algoritmo ####
def prog(iExec):
    global popA
    global popB
    global popC
    
    gl.custosIguais = 0
    gl.solCompl = 0
    
    gl.algStart = datetime.datetime.now() # Horário de Inicialização
    
    ### Inicializa Outputs de Convergência e de Atributos
    outputPopFolder = str(iExec)
    
    if not os.path.exists(gl.folder + "output\\"+outputPopFolder +"\\"): os.mkdir(gl.folder + "output\\"+outputPopFolder +"\\")
    if not os.path.exists(gl.folder+"output\\"+outputPopFolder+"\\gantt\\"): os.mkdir(gl.folder+"output\\"+str(outputPopFolder)+"\\gantt\\")
    
    fileConv = gl.folder+ "output\\"+outputPopFolder+"\\convergencia.txt"
    fileAtrib = gl.folder+ "output\\"+outputPopFolder+"\\atributos.txt"
    fileOutl = gl.folder+ "output\\"+outputPopFolder+"\\andamento.txt"
    
    #if os.path.exists(fileConv): os.remove(fileConv) # não deixar que o txt da convergencia seja reescrito
    #if os.path.exists(fileAtrib): os.remove(fileAtrib) # não deixar que o txt da convergencia seja reescrito
    #if os.path.exists(fileOutl): os.remove(fileOutl) # não deixar que o txt da convergencia seja reescrito
    
    conv = open(fileConv, 'w')
    atrib = open(fileAtrib, 'w')
    outl = open(fileOutl, 'w')
    conv.write("horario;iAlg;idSol mais barata;nViagens;nServs;custo;custoG;custoH")    
    atrib.write(str(gl.algStart)+';') #"horario inicio;iAlg;horario fim;delta horario\n"
    outl.write('Exec;Iteração;Sols Completas; Pop SizeViagSol max/min;Viagens Restantes a alocar ')
    conv.close()
    atrib.close()
    outl.close()
    
    

    ### INICIALIZA ALGORITMO ###
    iAlg = 0 
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
        popA = gl.inpop('A')
        popB = gl.inpop('B')
        popC = pp.Populacao(gl.nc, 'C')  
    
    ### EXECUTA LAÇO PRINCIPAL ###
    # Função Principal é chamada e tem como input e output as populações
    if gl.modo_fim == 0: # modo 0 - executa um numero finito de iterações
        for iAlg in range(1,gl.alg+1):
            gl.igl = iAlg
            popA,popB,popC = principal(popA,popB,popC, outputPopFolder)
            plot.outExec(fileOutl, iExec, popA.sizeViagSol(), popB.sizeViagSol(), popC.sizeViagSol(),popB.resta())
            plot.outConv(fileConv,popB.sols[popB.selecDet(1,[])[0]])
    elif gl.modo_fim ==1: #modo 1 - itera até atingir um certo numero de soluções completas
        gl.solCompl = 0 #contador de soluções completas já encontradas
        while gl.solCompl < gl.nCompl:
            iAlg = iAlg +1
            gl.igl = iAlg
            popA,popB,popC = principal(popA,popB,popC, outputPopFolder)
            plot.outExec(fileOutl, iExec, popA.sizeViagSol(), popB.sizeViagSol(), popC.sizeViagSol(),popB.resta())
            plot.outConv(fileConv,popB.sols[popB.selecDet(1,[])[0]])
    elif gl.modo_fim ==2: # modo 2 - itera até atingir alguma completa e tentar tryCompl iterações       
        gl.solCompl = 0
        gl.gotCompl = 0
        while gl.gotCompl < gl.tryCompl:
            iAlg = iAlg +1
            gl.igl = iAlg
            popA,popB,popC = principal(popA,popB,popC, outputPopFolder)
            plot.outExec(fileOutl, iExec, popA.sizeViagSol(), popB.sizeViagSol(), popC.sizeViagSol(),popB.resta())
            plot.outConv(fileConv,popB.sols[popB.selecDet(1,[])[0]])
        
            
    ### Finaliza algoritmo ###
    if gl.modo_salva == 1: guardaExecucao(popA,popB,popC, outputPopFolder) # guarda as populações num arquivo pickle para usar depois
    
    algEnd = datetime.datetime.now() # Horário de Finalização
    atrib = open(fileAtrib, 'a')
    atrib.write(str(gl.gotCompl)+';'+str(gl.igl)+';'+str(algEnd)+';'+str(algEnd-gl.algStart))  # Armazenar até qual iteração foi e quantas completas
    atrib.close()
    
    # plotar todos os gantts
    popA.gantt(outputPopFolder)
    popB.gantt(outputPopFolder)
    popC.gantt(outputPopFolder)
    if len(gl.popCompl.sols)>0 :gl.popCompl.gantt(outputPopFolder)
    #if len(gl.popQuase.sols)>0 :gl.popQuase.gantt(outputPopFolder)
    
    plot.convFinal(iExec)
    plot.folgasFinal(iExec, gl.popCompl)
    
