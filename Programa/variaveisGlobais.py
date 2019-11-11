# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 16:26:37 2019

@author: daniel.acosta
"""
import datetime as dtm
import pandas as pd
import classPopulacao as pp
import os


def colideHorario(i1,i2):    #funçao que testa se o horario das viagens colide (condiçao 1)   
    if vdict['hi'][i2]>=vdict['hi'][i1] and vdict['hi'][i2]<vdict['hf'][i1]: return True #início da v2 está dentro da v1, mas v1 continua
    elif vdict['hi'][i1]>=vdict['hi'][i2] and vdict['hi'][i1]<vdict['hf'][i2]: return True #início da v1 está dentro da v2, mas v2 continua
    elif vdict['hi'][i1] == vdict['hi'][i2] or vdict['hf'][i1] == vdict['hf'][i2]: #ambas coincidem em pelo menos um horário
        #print(i, "| Viagens comparadas têm mesmo hi ou hf.")
        #if vdict['ti'][i1] == vdict['ti'][i2] or vdict['tf'][i1] == vdict['tf'][i2]: #as viagens são idênticas!!!
            #print(i, "| Viagens comparadas têm mesmo ti ou tf")
        return True 
    else: return False #viagens não colidem
# Caminhos das Pastas
user = os.getlogin()
folder = "C:\\Users\\"+user+"\\Google Drive\\TCC Daniel Acosta\\GitHub\\genetic-algorithm-crew\\Programa\\"
inputViags = folder + "v_input.csv"
logf = open(folder + "output\\logfile.txt", 'w')

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
dfv.drop(columns="tab", inplace=True)   # excluir a coluna tab, porque aparentemente não vai mais ser necessário.
vdict = dfv.to_dict()

# PARÂMETROS

# Pesos dos custos
alfa = 1.5
delta = 0.5
tau = 1.5
gama = 4 
probabMaiorCusto = 0.08

# Populações
fs = 0.2
na = 10       #número de soluções na população A
nb = 5        #número de soluções na população B
nc = round(fs*na*(len(vdict['hi'])+na+nb))       #número de soluções na população C

pm = 0.02
nvInic = 1      #nº viagens a adicionar aleatoriamente na solução inicial
nCruz = 1       #nº soluções filhas adicionadas no cruzamento
nMut = 5        #nº soluções filhas adicionadas na mutação
nTop = 15       #nº soluções que sobrevivem na seleção Deterministica final
nRol = 10       #nº soluções que sobrevivem na seleção Roleta final
nCompl = 1      #nº soluções completas exigidas para que o algoritmo pare



# Listagens e Iteradores
alg = 100        #n° iterações do algoritmo (usar enquanto eu não estabelecer outro critério)

modo_inicio = 0  # 0 = do zero e salvar no binario / 1 = ler do binário e nao salvar
carregaPais = 0

idsGlob = 0     #contador de serviços global, para o identificador IDS

if modo_inicio==0: idsolGlob = 0   #contador de soluções global, para o identificador IDSOL
elif modo_inicio==1: idsolGlob = pp.inpop('id')

jornGlob = dtm.timedelta(hours = 7.5)  #duraçao fixa da jornada a considerar de início
duplicatas = 0
maiorSolucao = 0
custosIguais = 0

# População de Soluções Completas
popCompl = pp.Populacao(nCompl)



    

### CUSTO ############

dursViags = list(vdict['dur'].values())
durMediaViags = sum(dursViags, dtm.timedelta(0))/len(dursViags)
hmus = dtm.timedelta(hours=2) # 2h de intervalos (30min / 1h / 30min) - estimativa da folga mínima que se pode alcançar em um serviço
viagsPorServ = (jornGlob-hmus) / durMediaViags 

