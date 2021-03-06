"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""

import variaveisGlobais as gl

import pandas as pd
import plotly.express as px
import datetime

def convFinal(iExec): #plot da convergencia
    fileConv= open(gl.folder+ "output\\"+str(iExec)+"\\convergencia.txt")
    dfconv = pd.read_csv(fileConv, sep=';')
    xplot = list(dfconv['iAlg']) + list(dfconv['iAlg']) + list(dfconv['iAlg'])
    yplot = list(dfconv['custo'])+ list(dfconv['custoG'])+list(dfconv['custoH'])
    figconv = px.scatter(x=xplot, y=yplot)
    #figconv.show()
    figconv.write_image(gl.folder+"output\\"+str(iExec)+"\\convergencia.png")

def outConv(fileConv, sol): #csv da convergencia a cada iteração
    conv = open(fileConv, 'a')
    conv.write('\n'+str(datetime.datetime.now())+';'+str(gl.igl)+';'+str(sol.idsol)+';'+str(len(sol.viagSol))+';'+str(len(sol.servs))+';'+str(sol.custo().total_seconds())+';'+str(sol.custog().total_seconds())+';'+str(sol.custoh().total_seconds()))
    conv.close()
    
def outExec(fileOutl,iExec,sizea,sizeb,sizec,restantes): #informações de andamento que aparecem na tela, plota tanto na tela quanto num txt
    print('Execução '+ str(iExec) + ', Iteração ' + str(gl.igl)+ ' | '+str(len(gl.popCompl.sols))+' soluções completas | Pop SizeViagSol = max/min ~ A='+str(sizea)+', B='+str(sizeb)+', C='+str(sizec)+' | Restam '+str(restantes)+' viagens' ) 
    outl = open(fileOutl, 'a')
    outl.write('\n'+str(iExec)+';'+str(gl.igl)+';'+str(len(gl.popCompl.sols))+';'+str(sizea)+';'+str(sizeb)+';'+str(sizec)+';'+str(restantes))
    outl.close()

def folgasFinal(iExec, pop):
    fileFolgas= gl.folder+ "output\\"+str(iExec)+"\\folgas_"+str(pop.nome)+".txt"
    
    folg = open(fileFolgas, 'w')
    folg.write("População "+str(pop.nome))
    
    for sol in pop.sols:
        folgas = []
        ids = list(pop.sols[sol].servs)
        ids.sort(key= lambda idserv: pop.sols[sol].servs[idserv].jornI())
        folg.write("\nSolução "+str(pop.sols[sol].idsol))
        try:
            for serv in ids: folgas.append(pop.sols[sol].servs[serv].folgaE().total_seconds() + pop.sols[sol].servs[serv].folgaI().total_seconds())
            # salva em txt
            folg.write("\nidserv;folgaTotal")
            for i in len(ids): folg.write("\n"+str(ids[i])+";"+str(folgas[i]))
        except:
            folg.write("\nidserv;folgaTotal")
            folg.write("\n"+str(ids[0])+";"+str(pop.sols[sol].servs[ids[0]].folgaE().total_seconds() + pop.sols[sol].servs[ids[0]].folgaI().total_seconds()))
        
        # plota em imagem
        #figfolgas = px.scatter(x=xplot, y=yplot)
        #figfolgas.show()

    folg.close()