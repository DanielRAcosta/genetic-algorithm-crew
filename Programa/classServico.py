"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""

import datetime as dtm
import variaveisGlobais as gl

class Servico:
    def __init__(self, idvx):     #não tem como criar serviço sem viagem
    # só precisa, então, de uma viagem inicial (apenas seu INDEX)
        gl.idsGlob = gl.idsGlob +1    #adiciona ao contador global de serviços
        
        self.ids = gl.idsGlob      #identifica esse serviço
        self.jorn = gl.jornGlob    #por enquanto, utiliza a jornada globalmente definida de 7h30min.
        self.viags = [idvx]     #aqui não precisa ser guardada a viagem, só precisa guardar o index

    ############### BASE ####################    
    def atualizaViags(self,idvx):        #adiciona uma nova viagem a esse serviço, depois de já ter testado a viagem no testV.
        self.viags.append(idvx)
        self.sortV()       
    
    def sortV(self):
        self.viags.sort(key=lambda vx : gl.vdict['hi'][vx])

    ############# DURAÇÕES ##################    
    def hi(self):              #primeiro horario da primeira viagem alocada + tempo extra
        #talvez esse processamento aqui seja muito grande e seja melhor ir atualizando a cada vez que adiciona uma viagem.
        # ao mesmo tempo que verifica. e vai atualizando lá no init.
        hList = []
        for idvx in self.viags:
            #hiList.append(dfv.iloc[idvx-1,3]) #cria uma lista com todas as horas iniciais das viagens
            hList.append(gl.vdict['hi'][idvx])
        return min(hList)
    
    def hf(self):              #ultimo horario da ultima viagem alocada + tempo extra (quando add tempo extra cuidar aqui e na cabeJornada)
        hList = []
        #for i in range(len(self.viags)):
        for idvx in self.viags:
            #hfList.append(dfv.iloc[self.viags[i]-1,4]) #cria uma lista com todas as horas finais das viagens
            hList.append(gl.vdict['hf'][idvx])
        return max(hList)
    """tempo Extra no hi e no hf? Quando arrumar aqui, arrumar também em cabeJornada"""

    def condEf(self):          #calcula a condução efetiva - suponho que seja a soma de todas as durações de viagens
        durTotal = dtm.timedelta(0)
        for idvx in self.viags:
            durTotal = durTotal + gl.vdict['dur'][idvx]
        return durTotal

    def jornV(self):
        delta = self.hf()-self.hi()
        return delta


        # uma função que verifique se:
        # 1. a jornada já está completa, então não cabe mais nenhuma viagem
        # 2. no momento de inserção da viagem...

    ############ VERIFICAÇÕES ##############
    def cabeJornada(self,idvx): #checa se para realizar a viagem desejada, a jornada máxima não seria estourada
        # quando colocar os tempos extras do trabalhador chegar no deposito (fim e inicio de jornada), cuidar aqui também.
        """o que é mais rápido? ficar chamando os hi e hf toda hora ou guardar aqui no inicio?"""
        if gl.vdict['hi'][idvx]>self.hf(): #caso 1 - viagem nova no final do serviço
            if gl.vdict['hf'][idvx]-self.hi() < self.jorn:
                #print ("[CabeJornada] Caso 1 fim Return True")
                return True # CABE se mesmo colocando ela, não ultrapassa a jornada
            else:
                #print ("[CabeJornada] Caso 1 fim Return False")
                return False # NAO CABE - ultrapassou               
        elif gl.vdict['hf'][idvx]<self.hi(): #caso 2 - viagem nova no inicio do serviço
            if self.hf()-gl.vdict['hi'][idvx] < self.jorn:
                #print ("[CabeJornada] Caso 2 inicio Return True")
                return True # CABE
            else:
                #print ("[CabeJornada] Caso 2 inicio Return False")
                return False # NAO CABE
        elif gl.vdict['hi'][idvx]>self.hi() and gl.vdict['hf'][idvx]<self.hf():
            #print ("[CabeJornada] Caso 3 dentro Jornada Return True")
            return True # caso 3 - viagem nova dentro do serviço - não altera duração total
        else: #caso 4 - não atendidos nenhum dos anteriores
            # pela lógica, a nova viagem está colidindo (tem interseção) com a última do serviço.
            #print ("[CabeJornada] idv = ", idvx,", ids = ",self.ids," - A viagem colide.")
            return False
        
    def encaixaTerminal(self, idvx): #verifica se os terminais da viagem encaixam no serviço
        
        i_hs = [idv for idv in self.viags if gl.vdict['hf'][idv] < gl.vdict['hi'][idvx]]
        hs = [gl.vdict['hf'][idv] for idv in self.viags if gl.vdict['hf'][idv] < gl.vdict['hi'][idvx]]
        try:
            anterior = i_hs[hs.index(max(hs))]
            if gl.vdict['hf'][anterior]<=gl.vdict['hi'][idvx] and gl.vdict['tf'][anterior]==gl.vdict['ti'][idvx]:
                encaixa_ant = True
                #print("[encaixaTerminal] Viagem anterior encaixa")
            else:
                encaixa_ant = False 
                #print("[encaixaTerminal] Viagem anterior não encaixa")
        except:
            #print("[encaixaTerminal] Não há viagem anterior. Viagem adicionada no início do serviço.")
            encaixa_ant = True
            
        i_hs = [idv for idv in self.viags if gl.vdict['hi'][idv] > gl.vdict['hf'][idvx]]
        hs = [gl.vdict['hi'][idv] for idv in self.viags if gl.vdict['hi'][idv] > gl.vdict['hf'][idvx]]
        try:
            posterior = i_hs[hs.index(min(hs))]
            if gl.vdict['hf'][idvx]<=gl.vdict['hi'][posterior] and gl.vdict['tf'][idvx]==gl.vdict['ti'][posterior]:
                encaixa_post = True
                #print("[encaixaTerminal] Viagem posterior encaixa")
            else:
                encaixa_post = False 
                #print("[encaixaTerminal] Viagem posterior não encaixa.")
        except:
            #print("[encaixaTerminal] Não há viagem posterior. Viagem adicionada no fim do serviço.")
            encaixa_post = True

        return encaixa_ant and encaixa_post   
    
    #def testAlm:               
        # almoço, horario inicial e final dele, não precisam estar lá na inicialzação do serviço
        
    #def testJorn: