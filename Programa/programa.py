#%%
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

# INICIA O ALGORITMO #############################################################

modo_inicio = 1
# 0 = do zero / 1 = ler do binário

if modo_inicio == 0:
    popA = pp.Populacao(gl.na)
    popB = pp.Populacao(gl.nb)
    popC = pp.Populacao(gl.nc)
    
    # CRIA grupo de soluções iniciais A a partir de E - input = leitura de vdict, n populacao A (gl.na)
    for i in range(gl.na): popA.addSol(sl.Solucao(sv.Servico(rd.randrange(1,len(gl.vdict['hi'])+1))))
elif modo_inicio == 1:
    popA = pp.inpop('a')
    popB = pp.inpop('b')
    popC = pp.Populacao(gl.nc)

# INICIA O LAÇO PRINCIPAL #######################################################

for iAlg in range(gl.alg):
    popC.sols.clear() #esvazia B para recomeçar
    
    ### CRUZAMENTO ############
    # pra cada um dos nb melhores integrantes de A, de acordo com a função seleçãoDeterminística 
    for iSol in popA.selecDet(round(gl.fs*gl.na),[]):  # CRUZAMENTO B->C - repetir até gerar nCruz filhos cruzados dos pais de A
        # os pais dos cruzamentos aqui são buscados diretamente em A.
        for jSol in range(gl.nCruz): # cruza com E (vdict)
            ex = sl.Solucao(sv.Servico(popA.sols[iSol].viagNovaRandom())) # cria solução com viagem que ainda não existe em B
            popC.addSol(popA.sols[iSol].cruza(ex.viagSol)) #filho CE
            popC.addSol(ex.cruza(popA.sols[iSol].viagSol)) #filho EC
        
        for jSol in popA.selecRoleta(gl.nCruz,[]): #cruza com A
            popC.addSol(popA.sols[iSol].cruza(popA.sols[jSol].viagSol)) #filho CA
            popC.addSol(popA.sols[jSol].cruza(popA.sols[iSol].viagSol)) #filho AC
        
        if iAlg>0: #cruza com B
            for jSol in popB.selecRoleta(gl.nCruz,[]): 
                popC.addSol(popA.sols[iSol].cruza(popB.sols[jSol].viagSol)) #filho CB
                popC.addSol(popB.sols[jSol].cruza(popA.sols[iSol].viagSol)) #filho BC
                
        popC.addSol(popA.sols[iSol]) #só no final os pais advindos de A são adicionados à população, para que também sejam passíveis de mutação na próxima etapa
    
    ### MUTAÇÃO ############
    # antigo:
    #mutarSolucoes = popC.selecRand(gl.nMut, []) #quais soluções de B serão mutadas? deve ser declarado aqui para que o laço abaixo não gere soluções duplamente mutadas
    #for iSol in mutarSolucoes: popC.addSol(popC.sols[iSol].muta()) # adiciona à popB os filhos dos pais escolhidos acima 
    
    # novo: mutação substitui
    for iSol in popC.sols:
        if rd.random() < gl.pm: popC.sols[iSol].muta()
    
    # só para checar:
    idsolsC = [popC.sols[key].idsol for key in popC.sols]
    
    ### SELEÇÃO ############
    
    # deterministica C --> B
    idsolsB = [popB.sols[key].idsol for key in popB.sols] # lista de idsols das soluções que existem em C. deve entrar como argumento na função abaixo para evitar duplicatas
    melhores = popC.selecDet(gl.nTop,idsolsB) # retorna iterador com as keys das soluções escolhidas em B
    for iSol in melhores: popB.addSol(popC.sols[iSol]) # adiciona à população C as soluções escolhidas acima
    """ será que aqui a declaração está deletando algo? acho que não."""
    
    # roleta C --> A
    idsolsA = [popA.sols[key].idsol for key in popA.sols] # lista de idsols das soluções que existem em A. deve entrar como argumento na função abaixo para evitar duplicatas
    roleta = popC.selecRoleta(gl.nRol,idsolsA) # retorna iterador com as keys das soluções escolhidas em B
    for iSol in roleta: popA.addSol(popC.sols[iSol]) # adiciona à população A as soluções escolhidas acima
    
    # cortar deterministicamente as piores dos grupos constantes A & B
    popA.excluiDet()
    popB.excluiDet()

    # plota no arquivo output a cada iteração
    for sol in popC.sols:
        out = '\n' + str(iAlg) + ',' + str(sol) + ',' + str(popC.sols[sol].idsol) + ',' + str(popC.sols[sol].custog().total_seconds()) + ',' + str(popC.sols[sol].custoh().total_seconds()) + ',' + str(len(popC.sols[sol].servs)) + ',' + str(len(popC.sols[sol].viagSol))
        f.write(out)
    
    # plota na tela o número máximo de viagens
    print(iAlg, popA.sizeViagSol(), popB.sizeViagSol(), popC.sizeViagSol())

if modo_inicio == 0:
    pp.outpop(popA, 'a')    
    pp.outpop(popB, 'b')    
    pp.outpop(popC, 'c')    
#Fim do laço   
#%%
