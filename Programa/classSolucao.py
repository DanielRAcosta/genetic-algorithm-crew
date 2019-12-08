"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""

import variaveisGlobais as gl
import classServico as sv

import plotly.figure_factory as ff
import datetime as dtm
import random as rd
import numpy as np
import copy

class Solucao:
    def __init__(self, servx, idpais):  #não tem como criar uma solução sem serviço
        gl.idsolGlob = gl.idsolGlob + 1 #adiciona ao contador global de soluções
        
        self.idsol = gl.idsolGlob #identifica a solução atual
        self.servs = {0: servx}  #inicializa dicionario de serviços e insere o primeiro
        self.viagSol = copy.deepcopy(servx.viags) #copia lista de viagens do serviço para usar na solução
        self.idpais = idpais
        
    ### BASE ######

    def sortV(self): self.viagSol.sort(key=lambda vx : gl.vdict['hi'][vx])    

    def servIncompleto(self, serv, ok):
        if ok: gl.popQuase.addSolCheck(self.geraCopia())
        ok = False
        for vx in self.servs[serv].viags: self.viagSol.remove(vx)
        self.servs.pop(serv)
        return ok

    def completou(self): # checar se não está com serviços ruins!
        ok = True
                
        ids = list(self.servs)
        for serv in ids: #ALMOÇO INEXISTENTE?    
            if self.servs[serv].almI==None:
                self.servs[serv].tentaAtribuirAlmoco()
            if self.servs[serv].almI==None:    
                ok = self.servIncompleto(serv, ok)
        
        ids = list(self.servs)
        for serv in ids: #ALMOÇO EM HORARIO RUIM? - essa função está muito rígida
            if self.servs[serv].hi() + gl.minInicAlm + gl.intervPontaGlob > self.servs[serv].almI or self.servs[serv].hf() - gl.maxFimAlm - gl.intervPontaGlob <self.servs[serv].almF:
                ok = self.servIncompleto(serv, ok)
                
        ids = list(self.servs)
        for serv in ids: #POUCAS VIAGENS?
            if len(self.servs[serv].viags) < round(gl.viagsPorServ/2) -1:
                ok = self.servIncompleto(serv, ok)
                
        if ok:
            if gl.popCompl.addSolCheck(self.geraCopia()): #é adicionada uma cópia aqui, que vai ficar intocada. se deu True, adicionou
                gl.solCompl = gl.solCompl +1
                print("######################")
                print(gl.solCompl, " - Uma solução completa foi atingida. Cópia armazenada em popCompl.")

    def geraCopia(self):
        serv0filho = sv.Servico(0)
        idZero = list(self.servs.keys())[0]
        
        serv0filho.almF = copy.deepcopy(self.servs[idZero].almF)
        serv0filho.almI = copy.deepcopy(self.servs[idZero].almI)
        serv0filho.viags = copy.deepcopy(self.servs[idZero].viags)
        serv0filho.sortV()
        
        filho = Solucao(serv0filho, [self.idsol, 0])
                
        for jserv in list(self.servs.keys())[1:]:
            servxfilho = sv.Servico(0)
            servxfilho.almF = copy.deepcopy(self.servs[jserv].almF)
            servxfilho.almI = copy.deepcopy(self.servs[jserv].almI)
            servxfilho.viags = copy.deepcopy(self.servs[jserv].viags)
            servxfilho.sortV()
            filho.addServ(servxfilho)
            
        return filho

    def addServ(self, servx):   #adiciona um novo serviço a essa solução
        self.servs.update({list(self.servs.keys())[-1]+1 : servx}) # guarda o serviço no dicionario servs
        self.viagSol.extend(copy.deepcopy(servx.viags))
        self.sortV() #coloca as viagens em ordem ascendente
    
    def encaixaVSol(self,vx):
        adicionou = False
        j = 0 #para percorrer cada serviço da solução
        while adicionou == False and j<len(self.servs): # percorre cada serviço da solução até chegar ao fim da lista de serviços
            if self.servs[j].cabeJornada(vx): #não extrapola a soma de tempos 
                
                if self.servs[j].almI == None: # falta atribuir almoço?
                    if len(self.servs[j].viags)>gl.minViagAlm: # só se tiver no min duas viagens
                        self.servs[j].tentaAtribuirAlmoco()
                
                if self.servs[j].encaixaTerminal(vx): #terminais compativeis de bairro e centro
                    if self.servs[j].encaixaHorario(gl.vdict['hi'][vx],gl.vdict['hf'][vx]): #nao colide com nenhuma viagem  
                        if self.servs[j].colideAlmoco(vx): # se colide almoço
                            pass # melhoria futura: almoço flexível com a entrada da viagem
                            #if self.servs[j].encaixaViagAlmoco(vx): # tenta mesmo assim arrastar o almoço pro lado... se der add vx
                             #   self.servs[j].viags.append(vx)
                              #  self.servs[j].sortV()
                               # self.viagSol.append(vx)
                                #self.sortV()
                                #adicionou = True
                        
                        else: # se não colide
                            self.servs[j].viags.append(vx)
                            self.servs[j].sortV()
                            self.viagSol.append(vx)
                            self.sortV()
                            adicionou = True
                            
            j = j + 1
            
        if j == len(self.servs) and adicionou == False: #se chegou ao final da lista de serviços sem ter adicionado
            adicionou = True
            self.addServ(sv.Servico(vx))
        return adicionou

    def viagNovaRandom(self): # função que retorna uma viagem aleatória do vdict, mas apenas se ela já não existir na solução.
        if len(self.viagSol)<len(gl.vdict['hi']):
            notInSol = [vx for vx in gl.vdict['hi'] if vx not in self.viagSol]
            return notInSol[rd.randrange(len(notInSol))]
        else: 
            self.completou()
            return False

    ### GENÉTICOS ######
    
    def cruza(self, Pai2): #cruza duas soluções. gera um filho. entra a solução base e as viagens da solução a adicionar
        filho = self.geraCopia()
        filho.idpais[1] = Pai2.idsol
        
        notInSon = [vx for vx in Pai2.viagSol if vx not in filho.viagSol]
        
        if len(notInSon) > 0:
            for vx in notInSon:
                adicionou = filho.encaixaVSol(vx)
                if adicionou == False: print("ERRO ESTRANHÍSSIMO AO ENCAIXAR VIAGEM NA SOLUÇÃO")
            return filho, True # retorna aviso se deve ser adicionada como nova
        else: #Pai2 não provocou qualquer mudança em Base
            if len(filho.viagSol) == len(gl.vdict['hi']): self.completou()
            return filho, False
            #else: print("Solução Pai2 só tem viagens que já estão em Pai1, mas não está completa.")
        
    def muta(self):            #realiza mutação na solução atual. a aleatoriedade está fora dessa função, no bloco do código.
        if len(self.viagSol)<gl.algMutNeg*len(gl.vdict['hi']): self.mutaAdd()
        elif rd.random()<gl.probMutNeg: self.mutaDel()
        elif len(self.viagSol)<len(gl.vdict['hi']): self.mutaAdd()
        #else: solução na fase final do algoritmo, que não foi sorteada pra retirar viagem e que não pode receber viagem pois é completa
            
    def mutaAdd(self):
        vx = self.viagNovaRandom()
        adicionou = self.encaixaVSol(vx)
        if adicionou == False: print("ERRO ESTRANHÍSSIMO AO ENCAIXAR VIAGEM NA SOLUÇÃO")
        
    def mutaDel(self):
        print("mutaDel")
        serv = np.random.choice(list(self.servs), size=1, replace=False)[0]
        deleta = np.random.choice(self.servs[serv].viags, size=1, replace=False)[0]
        self.servs[serv].viags.remove(deleta)
        self.viagSol.remove(deleta)
        if self.servs[serv].viags == []: self.servs.pop(serv)
        
    #### CUSTOS ######

    def folgaI(self):
        folgaI = dtm.timedelta(0)
        for servx in self.servs: folgaI = folgaI + self.servs[servx].folgaI()
        return folgaI
    
    def folgaE(self):
        folgaE = dtm.timedelta(0)
        for servx in self.servs: folgaE = folgaE + self.servs[servx].folgaE()
        return folgaE
    
    def jorns(self):
        jorns = dtm.timedelta(0) 
        for servx in self.servs: jorns = jorns + self.servs[servx].jorn 
        return jorns
    
    def horaPico(self):
        horaPico = dtm.timedelta(0)
        for servx in self.servs: horaPico = horaPico + self.servs[servx].horaPico()
        return horaPico

    def custog(self): return gl.tau*self.folgaI() + self.folgaE() + gl.alfa*self.jorns() + gl.delta*self.horaPico() #custo g - custo da solução atual/existente
    
    def servFalta(self): return (len(gl.vdict['hi']) - len(self.viagSol)) / gl.viagsPorServ
    
    def custoh(self): return (self.servFalta() * gl.hmus + self.servFalta() * gl.alfa * gl.jornGlob)*gl.gama #custo h - penalidade relativa a "quanto falta para atingir uma suposta solução ótima"
        
    def custo(self): return self.custog() + self.custoh()           #determina o custo da solução atual de acordo com a tese de Elizondo
    
    def custotry(self): return [self.idsol, (gl.tau*self.folgaI() + self.folgaE() + gl.alfa*self.jorns()) + (self.servFalta() * gl.hmus + self.servFalta() * gl.alfa * gl.jornGlob) , self.folgaI(), self.folgaE(), self.jorns(), self.servFalta(), self.servFalta()*gl.hmus, self.servFalta() * gl.alfa * gl.jornGlob ]

    ### PRINTS ######
        
    def gantt(self, outputPopFolder, popname):
        df = []
        ids = list(self.servs)
        ids.sort(key= lambda idserv: self.servs[idserv].jornI())
        for serv in ids:
            if self.servs[serv].almI != None: df.append(dict(Task=str(serv), Start=self.servs[serv].almI, Finish=self.servs[serv].almF, Resource='Almoço'))
            df.extend([dict(Task=str(serv), Start=gl.vdict['hi'][vx], Finish=gl.vdict['hf'][vx], Resource='Viagens') for vx in self.servs[serv].viags])
            df.append(dict(Task=str(serv), Start =self.servs[serv].jornI(), Finish=self.servs[serv].jornI()+gl.intervPontaGlob, Resource='Recolhe'))
            df.append(dict(Task=str(serv), Start =self.servs[serv].jornF()-gl.intervPontaGlob, Finish=self.servs[serv].jornF(), Resource='Recolhe'))
            #df.append(dict(Task=str(serv), Start =self.servs[serv].jornI()+gl.intervPontaGlob, Finish=self.servs[serv].jornF()-gl.intervPontaGlob, Resource='Jornada'))
        
        titulo = "["+str(outputPopFolder)+"] pop"+popname+" - Sol "+str(self.idsol)+" - nViags "+str(len(self.viagSol))+" - Pais "+str(self.idpais[0])+" e "+str(self.idpais[1])+" - Folga Real "+str(round((self.folgaE().total_seconds()+self.folgaI().total_seconds())/3600,2))+"h"
        colors = dict(Viagens='rgb(219,0,0)', Almoço=(0.95,0.9,0.17), Recolhe='rgb(150,0,150)',Jornada='rgb(255,255,255)')
        
        fig = ff.create_gantt(df, colors=colors, index_col='Resource', show_colorbar=True, group_tasks=True, title=titulo)
        fig.write_image(gl.folder+"output\\"+str(outputPopFolder)+"\\gantt\\"+str(outputPopFolder)+"_pop"+popname+"_"+str(self.idsol)+".png")