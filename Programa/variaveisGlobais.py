# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 16:26:37 2019

@author: daniel.acosta
"""
import datetime as dtm
import pandas as pd
import classPopulacao as pp
#import plotly.express as px
import os

# Caminhos das Pastas
inputPopFolder = 'keep_20_11_3'
outputPopFolder = 'keep_20_11_3'

modo_inicio = 1     # 0 = do zero                       1 = ler do binário
modo_fim = 0        # 0 = até iAlg=alg                  1 = até ter nCompl soluções completas 
modo_salva = 1      # 0 = não salva no pickle           1 = salva no pickle
alg = 10000             # n° iterações do algoritmo (usar enquanto eu não estabelecer outro critério)
nCompl = 30         #nº soluções completas exigidas para que o algoritmo pare
carregaPais = 0     #se pais dos cruzamentos devem ser adicionados a C

# Pesos dos custos
alfa = 1.5
delta = 0.5
tau = 1.5
gama = 3.5 
probMaiorCusto = 0.08
probAlm = 0.5
probMutNeg = 0.9
algMutNeg = 0.8

# Populações
fs = 0.2        #fator de seleção ()   
na = 10         #número de soluções na população A
nb = 5         #número de soluções na população B
pm = 0.2        #probabilidade de mutação
nCruz = 1       #nº soluções filhas adicionadas no cruzamento
fatorTop = 0.3  #nº soluções que sobrevivem na seleção Deterministica final
fatorRol = 0.3  #nº soluções que sobrevivem na seleção Roleta final

jornGlob = dtm.timedelta(hours = 7.5)  #duraçao fixa da jornada a considerar de início
almGlob = dtm.timedelta(hours = 0.5)    #duracao fixa da colacao

user = os.getlogin()
folder = "C:\\Users\\"+ user+"\\Google Drive\\TCC Daniel Acosta\\GitHub\\genetic-algorithm-crew\\Programa\\"
#folder = os.getcwd()+'\\'
inputViags = folder + "v_input.csv"
logf = open(folder + "output\\logfile.txt", 'w')
wrRoleta = open(folder + "output\\wrRoletaCA.txt", 'w')
sols = open(folder+ "output\\solucoes.txt",'w')

# Contadores
if modo_inicio==0:
    idsolGlob = 0   #contador de soluções global, para o identificador IDSOL
    popCompl = pp.Populacao(nCompl, 'f') # População para guardar Soluções Completas
elif modo_inicio==1:
    idsolGlob = pp.inpop('id')
    popCompl = pp.inpop('f') # População para guardar Soluções Completas
custosIguais = 0
solCompl = 0

#%%

### LEITURA DO ARQUIVO DE INPUT ############
dfv = pd.read_csv(inputViags, sep=';', index_col=0) 
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

# PESO HORARIO DE PICO
start = min(dfv['hi'])
end = max(dfv['hf'])          

qtdVList = []
i = start

while i < end:
    qtdV = len([j for j in range(0,len(dfv)) if dfv.iloc[j,2] <= i and i <= dfv.iloc[j,3]])
    qtdVList.append(qtdV)
    i = i + dtm.timedelta(minutes=5)
    
maxq = max(qtdVList)
qtdVList = [(maxq-x)/maxq for x in qtdVList]

for j in range(0,len(dfv)):
    k = 0
    i = start
    while i < dfv.iloc[j,2]:
        i = i + dtm.timedelta(minutes=5)
        k = k + 1
    dfv.iloc[j,7] = qtdVList[k]    
            
dfv.drop(columns="tab", inplace=True)   # excluir a coluna tab, porque aparentemente não vai mais ser necessário.


#%%

vdict = dfv.to_dict()
nc = round(fs*na*(len(vdict['hi'])+na+nb))       #número de soluções na população C
dursViags = list(vdict['dur'].values())
durMediaViags = sum(dursViags, dtm.timedelta(0))/len(dursViags)
hmus = almGlob + dtm.timedelta(hours=1) # 2h de intervalos (30min / 1h / 30min) - estimativa da folga mínima que se pode alcançar em um serviço
viagsPorServ = (jornGlob-hmus) / durMediaViags 
meioTab = min(vdict['hi'].values()) + (max(vdict['hf'].values())-min(vdict['hi'].values()))/2


"""
def old_colideHorario(i1,i2):    #funçao que testa se o horario das viagens colide (condiçao 1)   
    if vdict['hi'][i2]>=vdict['hi'][i1] and vdict['hi'][i2]<vdict['hf'][i1]:
        #logf.write("\n[ColideHorario] Caso 1 - inicio da v2 está dentro da v1, mas v1 continua")
        return True #início da v2 está dentro da v1, mas v1 continua
    
    elif vdict['hi'][i1]>=vdict['hi'][i2] and vdict['hi'][i1]<vdict['hf'][i2]:
        #logf.write("\n[ColideHorario] Caso 2 - inicio da v1 está dentro da v2, mas v2 continua")
        return True #início da v1 está dentro da v2, mas v2 continua
    
    elif vdict['hi'][i1] == vdict['hi'][i2] or vdict['hf'][i1] == vdict['hf'][i2]: #ambas coincidem em pelo menos um horário
        #logf.write("\n[ColideHorario] Caso 3 - coincidem")
        #print(i, "| Viagens comparadas têm mesmo hi ou hf.")
        #if vdict['ti'][i1] == vdict['ti'][i2] or vdict['tf'][i1] == vdict['tf'][i2]: #as viagens são idênticas!!!
            #print(i, "| Viagens comparadas têm mesmo ti ou tf")
        return True 
    else: return False #viagens não colidem   
    
"""