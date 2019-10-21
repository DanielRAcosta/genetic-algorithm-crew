# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 16:26:37 2019

@author: daniel.acosta
"""
import datetime as dtm
import pandas as pd
import classPopulacao as pp

# PARAMETROS######################################################################3
# Controle do Algoritmo
na = 40       #população com que começa A
nb = 5        #população com que B permanece sempre
nc = 30       # 
nvInic = 1      #nº viagens a adicionar na solução inicial
nCruz = 1      #nº soluções filhas adicionadas no cruzamento
nMut = 5      #nº soluções filhas adicionadas na mutação
nTop = 10       #nº soluções que sobrevivem na seleção Deterministica final
nRol = 10
nCompl = 1      #nº soluções completas exigidas para que o algoritmo pare
alg = 1000        #n° iterações do algoritmo (usar enquanto eu não estabelecer outro critério)
# Listagem de Serviços e Soluções
idsGlob = 0     #contador de serviços global, para o identificador IDS
idsolGlob = 0   #contador de soluções global, para o identificador IDSOL
jornGlob = dtm.timedelta(hours = 7.5)  #duraçao fixa da jornada a considerar de início
# Pesos dos custos
alfa = 1.4
delta = 1
tau = 1
gama = 19
duplicatas = 0
maiorSolucao = 0
probabMaiorCusto = 0.08

inputPath = "C:\\Users\\Daniel\\Google Drive\\TCC Daniel Acosta\\Codigo\\Programa\\v_input.csv"
outputPath = "C:\\Users\\Daniel\\Google Drive\\TCC Daniel Acosta\\Codigo\\Programa\\alg_output.txt"

popCompl = pp.Populacao(nCompl)

def colideHorario(i1,i2):    #funçao que testa se o horario das viagens colide (condiçao 1)   
    if vdict['hi'][i2]>=vdict['hi'][i1] and vdict['hi'][i2]<vdict['hf'][i1]: return True #início da v2 está dentro da v1, mas v1 continua
    elif vdict['hi'][i1]>=vdict['hi'][i2] and vdict['hi'][i1]<vdict['hf'][i2]: return True #início da v1 está dentro da v2, mas v2 continua
    elif vdict['hi'][i1] == vdict['hi'][i2] or vdict['hf'][i1] == vdict['hf'][i2]: #ambas coincidem em pelo menos um horário
        #print(i, "| Viagens comparadas têm mesmo hi ou hf.")
        #if vdict['ti'][i1] == vdict['ti'][i2] or vdict['tf'][i1] == vdict['tf'][i2]: #as viagens são idênticas!!!
            #print(i, "| Viagens comparadas têm mesmo ti ou tf")
        return True 
    else: return False #viagens não colidem

#%% LEITURA DO ARQUIVO DE INPUT

dfv = pd.read_csv(inputPath, sep=';', index_col=0) 

for i in range(0,len(dfv)):             # Confusão absurda pra colocar a data na classe datetime de acordo com a tabela sábado ou sexta ou domingo
    if i==0:
        iniciodiai = 0
        iniciodiaf = 0
    else:
        if dfv.iloc[i,4]!=dfv.iloc[i-1,4] or dfv.iloc[i,5]!=dfv.iloc[i-1,5] or dfv.iloc[i,1]!=dfv.iloc[i-1,1]:
            iniciodiai = 0
            iniciodiaf = 0
            print(i, "| Começou nova tabela. |tab ", dfv['tab'][i],"|ti ", dfv['ti'][i],"|tf",dfv['tf'][i])
        else:
            if int(dfv.iloc[i,2][0:2])<dfv.iloc[i-1,2].hour:
                iniciodiai = 1
                print(i,"| Na mesma tabela, o dia virou em hi")
            if int(dfv.iloc[i,3][0:2])<dfv.iloc[i-1,3].hour:
                iniciodiaf = 1
                print(i, "| Na mesma tabela, o dia virou em hf")
    if dfv.iloc[i,1]==1: #tab 1 = segunda a sexta - 07 de junho de 2019
        diai = 7 + iniciodiai
        diaf = 7 + iniciodiaf
    elif dfv.iloc[i,1]==2: #tab 2 = sábado - 08 de junho de 2019
        diai = 8 + iniciodiai
        diaf = 8 + iniciodiaf
    elif dfv.iloc[i,1]==3: #tab 3 = domingo - 09 de junho de 2019
        diai = 9 + iniciodiai
        diaf = 9 + iniciodiaf
    else:
        print("Erro! A coluna TAB deve ser 1, 2 ou 3")
    dfv.iloc[i,2]=dtm.datetime(2019,6,diai,int(dfv.iloc[i,2][0:2]),int(dfv.iloc[i,2][3:5]),0)
    dfv.iloc[i,3]=dtm.datetime(2019,6,diaf,int(dfv.iloc[i,3][0:2]),int(dfv.iloc[i,3][3:5]),0)
    dfv.iloc[i,6]=dfv.iloc[i,3]-dfv.iloc[i,2]
    
dfv.drop(columns="tab", inplace=True)   # excluir a coluna tab, porque aparentemente não vai mais ser necessário.

vdict = dfv.to_dict()

#%% CUSTO

"""deve ser alterado quando for adicionado jornadas variaveis... esses custos todos talvez precisem entrar pra função custo da classe solução"""

dursViags = list(vdict['dur'].values())
durMediaViags = sum(dursViags, dtm.timedelta(0))/len(dursViags)
hmus = dtm.timedelta(hours=2) # 2h de intervalos (30min / 1h / 30min) - estimativa da folga mínima que se pode alcançar em um serviço
viagsPorServ = (jornGlob-hmus) / durMediaViags 
