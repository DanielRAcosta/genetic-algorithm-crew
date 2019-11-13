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

algStart = datetime.datetime.now()

conv = open(gl.folder+ "output\\convergencia.txt", 'w')
conv.write("\n################## EXECUÇÃO ÀS "+str(algStart)+" #################################")
conv.write("\n[POPB] iAlg,idSol mais barata,nViagens,nServs,custo,custoG,custoH")
conv.close()
gl.sols.write("[POPC] iAlg, sol, idSol, custoG [segundos], custoH [segundos], qtde Servs, qtde Viags, viags ")
gl.wrRoleta.write("### ROLETA C-A ## - execução às "+str(algStart))


### INICIA O ALGORITMO ######

if gl.modo_inicio == 0:
    popA = pp.Populacao(gl.na)
    popB = pp.Populacao(gl.nb)
    popC = pp.Populacao(gl.nc)
    
    # CRIA grupo de soluções iniciais A a partir de E - input = leitura de vdict, n populacao A (gl.na)
    randlist = []
    for i in range(gl.na):
        vx = rd.randrange(1,len(gl.vdict['hi'])+1)
        while vx in randlist: vx = rd.randrange(1,len(gl.vdict['hi'])+1)
        randlist.append(vx)
        
    for vx in randlist: popA.addSol(sl.Solucao(sv.Servico(vx)))
    
    gl.logf.write("\npopA aleatória inicial criada com as viagens "+str(randlist))
        
elif gl.modo_inicio == 1:
    popA = pp.inpop('a')
    popB = pp.inpop('b')
    popC = pp.Populacao(gl.nc)
    gl.logf.write("\npopA e popB obtidas do pickle.")
    
gl.logf.write("\nInicia o Laço Principal.")

### DEFINE O LAÇO PRINCIPAL (para executar depois) ######

def principal():
    #popA.gantt(iAlg) #plot gantt image
    popC.sols.clear() #esvazia B para recomeçar
    gl.logf.write("\n######Iteração "+str(iAlg)+"######")
    
    ### CRUZAMENTO ############
    # pra cada um dos nb melhores integrantes de A, de acordo com a função seleçãoDeterminística 
    for iSol in popA.selecDet(round(gl.fs*gl.na),[]):  # CRUZAMENTO B->C - repetir até gerar nCruz filhos cruzados dos pais de A
        gl.logf.write("\nCruzamento - Pai1 id "+str(iSol)+" com viagens "+str(popA.sols[iSol].viagSol))
        # os pais dos cruzamentos aqui são buscados diretamente em A.
        for jSol in range(gl.nCruz): # cruza com E (vdict)
            ex = sl.Solucao(sv.Servico(popA.sols[iSol].viagNovaRandom())) # cria solução com viagem que ainda não existe em B
            gl.logf.write("\n[popC "+str(len(popC.sols))+" Cruzamento com E - Pai2 id "+str(ex.idsol)+" com viagens "+str(ex.viagSol))
            
            
            filho = popA.sols[iSol].cruza(ex.viagSol) 
            gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho CE id "+str(filho.idsol)+" com viagens "+str(filho.viagSol))
            popC.addSol(filho) #filho CE
            gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho CE adicionado a popC.")
            
            filho2 = ex.cruza(popA.sols[iSol].viagSol)
            gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho EC id "+str(filho2.idsol)+" com viagens "+str(filho2.viagSol))
            popC.addSolCheck(filho2)
            
        for jSol in popA.selecRoleta(gl.nCruz,pais1): #cruza com A
            gl.logf.write("\n[popC "+str(len(popC.sols))+" Cruzamento com A - Pai2 id "+str(jSol)+" com viagens "+str(popA.sols[jSol].viagSol))
            
            filho = popA.sols[iSol].cruza(popA.sols[jSol].viagSol)
            gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho CA id "+str(filho.idsol)+" com viagens "+str(filho.viagSol))
            popC.addSolCheck(filho)                
            
            filho2 = popA.sols[jSol].cruza(popA.sols[iSol].viagSol)
            gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho AC id "+str(filho2.idsol)+" com viagens "+str(filho2.viagSol))
            popC.addSolCheck(filho2)
        
        
        if iAlg>0: #cruza com B
            for jSol in popB.selecRoleta(gl.nCruz,[]): 
                gl.logf.write("\n[popC "+str(len(popC.sols))+" Cruzamento com B - Pai2 id "+str(jSol)+" com viagens "+str(popB.sols[jSol].viagSol))
                
                filho = popA.sols[iSol].cruza(popB.sols[jSol].viagSol)
                gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho CB id "+str(filho.idsol)+" com viagens "+str(filho.viagSol))
                popC.addSolCheck(filho) #filho CB
                
                filho2 = popB.sols[jSol].cruza(popA.sols[iSol].viagSol)
                gl.logf.write("\n[popC "+str(len(popC.sols))+"] Filho BC id "+str(filho2.idsol)+" com viagens "+str(filho2.viagSol))
                popC.addSolCheck(filho2)
            
        if gl.carregaPais == 1: popC.addSolCheck(popA.sols[iSol])
        #só no final os pais advindos de A são adicionados à população, para que também sejam passíveis de mutação na próxima etapa

    # EXCLUI deterministicamente/roleta? as piores dos grupos constantes A & B
    popA.excluiRol()
    popB.excluiRol()
    
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
    
    gl.wrRoleta = open(gl.folder+"output\\wrRoletaCA.txt",'a')
    gl.wrRoleta.write("\n"+str(iAlg)+',')
    # roleta C --> A
    idsolsA = [popA.sols[key].idsol for key in popA.sols] # lista de idsols das soluções que existem em A. deve entrar como argumento na função abaixo para evitar duplicatas
    roleta = popC.selecRoleta(gl.nRol,idsolsA) # retorna iterador com as keys das soluções escolhidas em B
    for iSol in roleta: popA.addSol(popC.sols[iSol]) # adiciona à população A as soluções escolhidas acima
    if erroRoleta: gl.logf.write("\n["+str(iAlg)+"] Roleta recebeu custos iguais na seleção final popC-->popA, portanto a escolha é sem pesos. ")
    
    
    #plot custo popB mínimo custo
    best = popB.selecDet(1,[])[0]
    conv = open(gl.folder+ "output\\convergencia.txt", 'a')
    conv.write('\n'+str(iAlg)+','+str(popB.sols[best].idsol)+','+str(len(popB.sols[best].viagSol))+','+str(len(popB.sols[best].servs))+','+str(popB.sols[best].custo().total_seconds())+','+str(popB.sols[best].custog().total_seconds())+','+str(popB.sols[best].custoh().total_seconds()))
    #ialg - sol min custo - nviag - nserv - custo - custo g - custo h 
    conv.close()
    
    for sol in popC.sols:
        out = '\n' + str(iAlg) + ',' + str(sol) + ',' + str(popC.sols[sol].idsol) + ',' + str(popC.sols[sol].custog().total_seconds()) + ',' + str(popC.sols[sol].custoh().total_seconds()) + ',' + str(len(popC.sols[sol].servs)) + ',' + str(len(popC.sols[sol].viagSol)) + ',' + str(popC.sols[sol].viagSol)
        gl.logf.write(out)
    #plot all text
    #popA.wrpop(iAlg)
    #popB.wrpop(iAlg)
    #popC.wrpop(iAlg)
    
    # plota na tela o número máximo de viagens
    print(iAlg, popA.sizeViagSol(), popB.sizeViagSol(), popC.sizeViagSol())

if gl.modo_inicio == 0:
    #plot gantt image
    #popC.gantt(iAlg)
    #popB.gantt(iAlg)
       
    
#### EXECUTA O LAÇO PRINCIPAL ####
    
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
if gl.modo_salva == 1:
    pp.outpop(popA, 'a')    
    pp.outpop(popB, 'b')    
    pp.outpop(popC, 'c')    
    pp.outpop(gl.popCompl, 'f')
    pp.outpop(gl.idsolGlob, 'id')
    
algEnd = datetime.datetime.now()
gl.logf.write("Algoritmo executado em "+str(algEnd-algStart))