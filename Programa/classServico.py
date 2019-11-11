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
    def sortV(self): self.viags.sort(key=lambda vx : gl.vdict['hi'][vx])

    ############# DURAÇÕES ##################    
    def hi(self):              #primeiro horario da primeira viagem alocada + tempo extra
        hList = [gl.vdict['hi'][vx] for vx in self.viags] #cria uma lista com todas as horas iniciais das viagens    
        return min(hList)
    
    def hf(self):      #ultimo horario da ultima viagem alocada + tempo extra (quando add tempo extra cuidar aqui e na cabeJornada)
        hList = [gl.vdict['hf'][vx] for vx in self.viags]
        return max(hList)

    def condEf(self):          #calcula a condução efetiva - suponho que seja a soma de todas as durações de viagens
        durTotal = dtm.timedelta(0)
        for idvx in self.viags: durTotal = durTotal + gl.vdict['dur'][idvx]
        return durTotal

    def jornV(self): return self.hf()-self.hi()
        # uma função que verifique se:
        # 1. a jornada já está completa, então não cabe mais nenhuma viagem
        # 2. no momento de inserção da viagem...

    ############ VERIFICAÇÕES ##############
    def cabeJornada(self,idvx): #checa se para realizar a viagem desejada, a jornada máxima não seria estourada
        # quando colocar os tempos extras do trabalhador chegar no deposito (fim e inicio de jornada), cuidar aqui também.
        if gl.vdict['hi'][idvx]>self.hf(): #caso 1 - viagem nova no final do serviço
            if gl.vdict['hf'][idvx]-self.hi() < self.jorn:
                #gl.logf.write("\n[cabeJornada] True Caso 1 - viagem cabe no final do serviço")
                return True # CABE se mesmo colocando ela, não ultrapassa a jornada
            else:
                #gl.logf.write("\n[cabeJornada] False Caso 1 - viagem muito tarde")
                return False # NAO CABE - ultrapassou               
        elif gl.vdict['hf'][idvx]<self.hi(): #caso 2 - viagem nova no inicio do serviço
            if self.hf()-gl.vdict['hi'][idvx] < self.jorn:
                #gl.logf.write("\n[cabeJornada] True Caso 2 - viagem cabe no início do serviço")
                return True # CABE
            else:
                #gl.logf.write("\n[cabeJornada] False Caso 2 - viagem muito cedo")
                return False # NAO CABE
        elif gl.vdict['hi'][idvx]>self.hi() and gl.vdict['hf'][idvx]<self.hf():
            #gl.logf.write("\n[cabeJornada] True Caso 3 - viagem cabe no meio do serviço")
            return True # caso 3 - viagem nova dentro do serviço - não altera duração total
        else:
            #gl.logf.write("\n[cabeJornada] False Caso 3 - viagem colide")
            return False # pela lógica, a nova viagem está colidindo (tem interseção) com a última do serviço.
                
    def encaixaTerminal(self, idvx): #verifica se os terminais da viagem encaixam no serviço
        i_hs = [idv for idv in self.viags if gl.vdict['hf'][idv] < gl.vdict['hi'][idvx]]
        hs = [gl.vdict['hf'][idv] for idv in self.viags if gl.vdict['hf'][idv] < gl.vdict['hi'][idvx]]
        try:
            anterior = i_hs[hs.index(max(hs))]
            if gl.vdict['hf'][anterior]<=gl.vdict['hi'][idvx] and gl.vdict['tf'][anterior]==gl.vdict['ti'][idvx]:
                encaixa_ant = True
                #gl.logf.write("\n[encaixaTerm] Encaixa Anterior True")
            else:
                encaixa_ant = False 
                #gl.logf.write("\n[encaixaTerm] Encaixa Anterior False")
        except:
            encaixa_ant = True
            #gl.logf.write("\n[encaixaTerm] Encaixa Anterior True - não existe viagem antes, então encaixa")
            
        i_hs = [idv for idv in self.viags if gl.vdict['hi'][idv] > gl.vdict['hf'][idvx]]
        hs = [gl.vdict['hi'][idv] for idv in self.viags if gl.vdict['hi'][idv] > gl.vdict['hf'][idvx]]
        try:
            posterior = i_hs[hs.index(min(hs))]
            if gl.vdict['hf'][idvx]<=gl.vdict['hi'][posterior] and gl.vdict['tf'][idvx]==gl.vdict['ti'][posterior]:
                encaixa_post = True
                #gl.logf.write("\n[encaixaTerm] Encaixa Posterior True")
            else:
                encaixa_post = False 
                #gl.logf.write("\n[encaixaTerm] Encaixa Posterior False")
        except:
            encaixa_post = True
            #gl.logf.write("\n[encaixaTerm] Encaixa Posterior False - não viagem antes, então encaixa")

        #gl.logf.write("\n[encaixaTerm] Encaixa Final "+ str( encaixa_ant and encaixa_post))
        return encaixa_ant and encaixa_post   
    
    #def testAlm:               
        # almoço, horario inicial e final dele, não precisam estar lá na inicialzação do serviço
        
    #def testJorn: