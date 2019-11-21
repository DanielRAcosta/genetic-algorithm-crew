"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""

import random as rd
import classServico as sv
import classSolucao as sl
import classPopulacao as pp
import variaveisGlobais as gl

import numpy as np
import math
import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style


algStart = datetime.datetime.now()

#conv = open(gl.folder+ "output\\convergencia.txt", 'w')
#onv.write("\n################## EXECUÇÃO ÀS "+str(algStart)+" #################################")
#conv.write("\n[POPB] iAlg,idSol mais barata,nViagens,nServs,custo,custoG,custoH")
#conv.close()
gl.sols.write("[POPC] iAlg, sol, idSol, custoG [segundos], custoH [segundos], qtde Servs, qtde Viags, viags ")
gl.wrRoleta.write("### ROLETA C-A ## - execução às "+str(algStart))


### INICIA O ALGORITMO ######

style.use('fivethirtyeight')
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = fig.add_subplot(1,1,1)
ax3 = fig.add_subplot(1,1,1)
ax4 = fig.add_subplot(1,1,1)
ax5 = fig.add_subplot(1,1,1)
                  
                  
if gl.modo_inicio == 0:
    popA = pp.Populacao(gl.na, 'A')
    popB = pp.Populacao(gl.nb, 'B')
    popC = pp.Populacao(gl.nc, 'C')
    
    # CRIA grupo de soluções iniciais A a partir de E - input = leitura de vdict, n populacao A (gl.na)
    randlist = []
    for i in range(gl.na):
        vx = rd.randrange(1,len(gl.vdict['hi'])+1)
        while vx in randlist: vx = rd.randrange(1,len(gl.vdict['hi'])+1)
        randlist.append(vx)
        
    for vx in randlist: popA.addSol(sl.Solucao(sv.Servico(vx), [0,0]))
    
    gl.logf.write("\npopA aleatória inicial criada com as viagens "+str(randlist))
        
elif gl.modo_inicio == 1:
    popA = pp.inpop('A')
    popB = pp.inpop('B')
    popC = pp.Populacao(gl.nc, 'C')
    gl.logf.write("\npopA e popB obtidas do pickle.")
    
gl.logf.write("\nInicia o Laço Principal.")

### DEFINE O LAÇO PRINCIPAL (para executar depois) ######
def guardaExecucao():
    global popA
    global popB
    global popC

    pp.outpop(popA, 'a')    
    pp.outpop(popB, 'b')    
    pp.outpop(popC, 'c')    
    #pp.outpop(gl.popCompl, 'f')
    pp.outpop(gl.idsolGlob, 'id')
    
def animate(i):
    global ax1
    global ax2
    global ax3
    global ax4
    global ax5
    
    
    graph_data = open(gl.folder+ "output\\convergencia.txt",'r').read()
    lines = graph_data.split('\n')
    xv = []
    xs = []
    xc = []
    xg = []
    xh = []
    ys = []
    for line in lines:
        if len(line) > 1:
            [i, idSolp, nvp, nsp, cp, cg, ch] = line.split(',')
            xv.append(float(nvp))
            xs.append(float(nsp))
            xc.append(float(cp))
            xg.append(float(cg))
            xh.append(float(ch))
            ys.append(float(i))
    ax1.clear()
    ax2.clear()
    ax3.clear()
    ax4.clear()
    ax5.clear()
    ax1.plot(ys, xv)
    ax2.plot(ys, xs)
    ax3.plot(ys, xc)
    ax4.plot(ys, xg)
    ax5.plot(ys, xh)

def principal():
    #popA.gantt(iAlg) #plot gantt image
    popC.sols.clear() #esvazia B para recomeçar
    gl.logf.write("\n### Iteração "+str(iAlg)+"######")
    
    ### CRUZAMENTO ############
    # pra cada um dos nb melhores integrantes de A, de acordo com a função seleçãoDeterminística 
    pais1 = popA.selecDet(round(gl.fs*gl.na),[])
    for iSol in pais1:  # CRUZAMENTO B->C - repetir até gerar nCruz filhos cruzados dos pais de A
        #gl.logf.write("\nCruzamento - Pai1 id "+str(iSol)+" com viagens "+str(popA.sols[iSol].viagSol))
        # os pais dos cruzamentos aqui são buscados diretamente em A.
        
        for jSol in range(gl.nCruz): # cruza com E (vdict)
            vx = popA.sols[iSol].viagNovaRandom()
            if vx is not False: 
                ex = sl.Solucao(sv.Servico(vx), [0,0]) # cria solução com viagem que ainda não existe em B
                #gl.logf.write("\n[popC "+str(len(popC.sols))+" Cruzamento com E - Pai2 id "+str(ex.idsol)+" com viagens "+str(ex.viagSol))
                
                #filho CE
                filho, alterou = popA.sols[iSol].cruza(ex) 
                #gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho CE id "+str(filho.idsol)+" com viagens "+str(filho.viagSol))
                if alterou: popC.addSol(filho)
            #gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho CE adicionado a popC.")
            
            #filho EC
                filho2, alterou = ex.cruza(popA.sols[iSol])
            #gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho EC id "+str(filho2.idsol)+" com viagens "+str(filho2.viagSol))
                if alterou: popC.addSolCheck(filho2)
            
        for jSol in popA.selecRoleta(gl.nCruz,pais1)[0]: #cruza com A
            #gl.logf.write("\n[popC "+str(len(popC.sols))+" Cruzamento com A - Pai2 id "+str(jSol)+" com viagens "+str(popA.sols[jSol].viagSol))
            
            #filho CA
            filho, alterou = popA.sols[iSol].cruza(popA.sols[jSol])
            #gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho CA id "+str(filho.idsol)+" com viagens "+str(filho.viagSol))
            if alterou: popC.addSolCheck(filho)                
            
            #filho AC
            filho2, alterou = popA.sols[jSol].cruza(popA.sols[iSol])
            #gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho AC id "+str(filho2.idsol)+" com viagens "+str(filho2.viagSol))
            if alterou: popC.addSolCheck(filho2)
        
        
        if iAlg+gl.modo_inicio>1: #cruza com B
            for jSol in popB.selecRoleta(gl.nCruz,[])[0]: 
                #gl.logf.write("\n[popC "+str(len(popC.sols))+" Cruzamento com B - Pai2 id "+str(jSol)+" com viagens "+str(popB.sols[jSol].viagSol))
                
                #filho CB
                filho, alterou = popA.sols[iSol].cruza(popB.sols[jSol])
                #gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho CB id "+str(filho.idsol)+" com viagens "+str(filho.viagSol))
                if alterou: popC.addSolCheck(filho)
                
                #filho BC
                filho2, alterou = popB.sols[jSol].cruza(popA.sols[iSol])
                #gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho BC id "+str(filho2.idsol)+" com viagens "+str(filho2.viagSol))
                if alterou: popC.addSolCheck(filho2)
            
        if gl.carregaPais == 1: popC.addSolCheck(popA.sols[iSol])
        #só no final os pais advindos de A são adicionados à população, para que também sejam passíveis de mutação na próxima etapa
        
        if gl.carregaPais == 0 and popC.sols == {}:
            popC.addSolCheck(popA.sols[iSol])
            choice = np.random.choice(list(popC.sols), size=1, replace=False)[0]
            popC.sols[choice].muta()
        

    # EXCLUI deterministicamente/roleta? as piores dos grupos constantes A & B
    popA.excluiRol()
    popB.excluiRol()
    gl.popCompl.excluiRol()
    
    ### MUTAÇÃO ############    
    for iSol in popC.sols: # novo: mutação substitui
        if rd.random() < gl.pm:
            popC.sols[iSol].muta()
            print("muta ",iSol)
    
    ### SELEÇÃO ############
    
    # deterministica C --> B
    idsolsB = [popB.sols[key].idsol for key in popB.sols] # lista de idsols das soluções que existem em B. deve entrar como argumento na função abaixo para evitar duplicatas
    melhores = popC.selecDet(math.ceil(gl.fatorTop*len(popC.sols)),idsolsB) # retorna iterador com as keys das soluções escolhidas em C
    for iSol in melhores: popB.addSolCheck(popC.sols[iSol]) # adiciona à população B as soluções escolhidas acima
    
    gl.wrRoleta = open(gl.folder+"output\\wrRoletaCA.txt",'a')
    gl.wrRoleta.write("\n"+str(iAlg)+',')
    # roleta C --> A
    idsolsA = [popA.sols[key].idsol for key in popA.sols] # lista de idsols das soluções que existem em A. deve entrar como argumento na função abaixo para evitar duplicatas
    roleta, erroRoleta = popC.selecRoleta(math.floor(gl.fatorRol*len(popC.sols)),idsolsA) # retorna iterador com as keys das soluções escolhidas em B
    for iSol in roleta: popA.addSolCheck(popC.sols[iSol]) # adiciona à população A as soluções escolhidas acima
    if erroRoleta: gl.logf.write("\n["+str(iAlg)+"] Roleta recebeu custos iguais na seleção final popC-->popA, portanto a escolha é sem pesos. ")
    
    ### SAÍDA DE DADOS #####
       
    # plota na tela o número máximo de viagens
    print(iAlg, popA.sizeViagSol(), popB.sizeViagSol(), popC.sizeViagSol())
    
    #plot custo popB mínimo custo
    best = popB.selecDet(1,[])[0]
    conv = open(gl.folder+ "output\\convergencia.txt", 'a')
    conv.write('\n'+str(iAlg)+','+str(popB.sols[best].idsol)+','+str(len(popB.sols[best].viagSol))+','+str(len(popB.sols[best].servs))+','+str(popB.sols[best].custo().total_seconds())+','+str(popB.sols[best].custog().total_seconds())+','+str(popB.sols[best].custoh().total_seconds()))
    #ialg - sol min custo - nviag - nserv - custo - custo g - custo h 
    conv.close()
    
        
    #plot ao vivo
    if float(iAlg/30).is_integer() and gl.modo_salva == 1: guardaExecucao()
    
    if float(iAlg/30).is_integer():            
        ani = animation.FuncAnimation(fig, animate, interval=1000)
        plt.show()    
    
    #plot all text
    #popA.wrpop(iAlg)
    #popB.wrpop(iAlg)
    #popC.wrpop(iAlg)
    
    #plot gantt image
    #popC.gantt(iAlg)
    #popB.gantt(iAlg)
       
    
    
    
    
#### EXECUTA O LAÇO PRINCIPAL ######################################
    
if gl.modo_fim == 0: # modo 0 - executa um numero finito de iterações
    for iAlg in range(1,gl.alg+1):
        principal()  
        
elif gl.modo_fim ==1: #modo 1 - itera até atingir um certo numero de soluções completas
    iAlg = 0  
    gl.solCompl = 0
    while gl.solCompl < gl.nCompl:
        iAlg = iAlg +1
        principal()
        
# guarda as populações num arquivo pickle para usar depois
if gl.modo_salva == 1: guardaExecucao()

    
algEnd = datetime.datetime.now()
gl.logf.write("Algoritmo executado em "+str(algEnd-algStart))