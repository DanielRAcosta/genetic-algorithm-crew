"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""

import variaveisGlobais as gl

import pandas as pd
import plotly.express as px

def conv(iExec):
    fileConv= open(gl.folder+ "output\\"+str(iExec)+"\\convergencia.txt")
    dfconv = pd.read_csv(fileConv, sep=',')
    xplot = list(dfconv['iAlg']) + list(dfconv['iAlg']) + list(dfconv['iAlg'])
    yplot = list(dfconv['custo'])+ list(dfconv['custoG'])+list(dfconv['custoH'])
    figconv = px.scatter(x=xplot, y=yplot)
    figconv.show()