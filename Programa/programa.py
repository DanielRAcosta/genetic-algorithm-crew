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

popA = pp.Populacao(gl.na)
popB = pp.Populacao(gl.nb)
popC = pp.Populacao(gl.nc)

f = open(gl.outputPath, 'w')

# INICIA O ALGORITMO #############################################################

# CRIA grupo de soluções iniciais A a partir de E - input = leitura de vdict, n populacao A (gl.na)
for i in range(gl.na): popA.addSol(sl.Solucao(sv.Servico(rd.randrange(1,len(gl.vdict['hi'])+1))))

# INICIA O LAÇO PRINCIPAL #######################################################

for iAlg in range(gl.alg):
    popB.sols.clear() #esvazia B para recomeçar
    
    ### CRUZAMENTO ############
    # pra cada um dos nb melhores integrantes de A, de acordo com a função seleçãoDeterminística 
    for iSol in popA.selecDet(gl.nb,[]):  # CRUZAMENTO B->C - repetir até gerar nCruz filhos cruzados dos pais de A
        # os pais dos cruzamentos aqui são buscados diretamente em A.
        for jSol in range(gl.nCruz): # cruza com vdict
            ex = sl.Solucao(sv.Servico(popA.sols[iSol].viagNovaRandom())) # cria solução com viagem que ainda não existe em B
            popB.addSol(popA.sols[iSol].cruza(ex.viagSol)) #filho BE
            popB.addSol(ex.cruza(popA.sols[iSol].viagSol)) #filho EB
        
        for jSol in popA.selecRoleta(gl.nCruz,[]): #cruza com A
            popB.addSol(popA.sols[iSol].cruza(popA.sols[jSol].viagSol)) #filho BA
            popB.addSol(popA.sols[jSol].cruza(popA.sols[iSol].viagSol)) #filho AB
        
        if iAlg>0: #cruza com C
            for jSol in popC.selecRoleta(gl.nCruz,[]): 
                popB.addSol(popA.sols[iSol].cruza(popC.sols[jSol].viagSol)) #filho BD
                popB.addSol(popC.sols[jSol].cruza(popA.sols[iSol].viagSol)) #filho DB
                
        popB.addSol(popA.sols[iSol]) #só no final os pais advindos de A são adicionados à população, para que também sejam passíveis de mutação na próxima etapa
    
    ### MUTAÇÃO ############
    mutarSolucoes = popB.selecRand(gl.nMut, []) #quais soluções de B serão mutadas? deve ser declarado aqui para que o laço abaixo não gere soluções duplamente mutadas
    for iSol in mutarSolucoes: popB.addSol(popB.sols[iSol].muta()) # adiciona à popB os filhos dos pais escolhidos acima 
    
    # só para checar:
    idsolsB = [popB.sols[key].idsol for key in popB.sols]
    
    ### SELEÇÃO ############
    
    # deterministica B --> C
    idsolsC = [popC.sols[key].idsol for key in popC.sols] # lista de idsols das soluções que existem em C. deve entrar como argumento na função abaixo para evitar duplicatas
    melhores = popB.selecDet(gl.nTop,idsolsC) # retorna iterador com as keys das soluções escolhidas em B
    for iSol in melhores: popC.addSol(popB.sols[iSol]) # adiciona à população C as soluções escolhidas acima
    
    # roleta B --> A
    idsolsA = [popA.sols[key].idsol for key in popA.sols] # lista de idsols das soluções que existem em A. deve entrar como argumento na função abaixo para evitar duplicatas
    roleta = popB.selecRoleta(gl.nRol,idsolsA) # retorna iterador com as keys das soluções escolhidas em B
    for iSol in roleta: popA.addSol(popB.sols[iSol]) # adiciona à população A as soluções escolhidas acima
    
    # cortar as piores dos grupos constantes A & C
    popA.excluiDet()
    popC.excluiDet()

    # plota no arquivo output a cada iteração
    for sol in popC.sols:
        out = '\n' + str(iAlg) + ',' + str(sol) + ',' + str(popC.sols[sol].idsol) + ',' + str(popC.sols[sol].custog().total_seconds()) + ',' + str(popC.sols[sol].custoh().total_seconds()) + ',' + str(len(popC.sols[sol].servs)) + ',' + str(len(popC.sols[sol].viagSol))
        f.write(out)
    
    # plota na tela o número máximo de viagens
    print(iAlg, popA.maxViagSol(), popB.maxViagSol(), popC.maxViagSol())
    
#Fim do laço   
#%%
