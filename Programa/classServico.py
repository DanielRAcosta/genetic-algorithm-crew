"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""
import datetime as dtm
#import math
import variaveisGlobais as gl

class Servico:
    def __init__(self, idvx):     #não tem como criar serviço sem viagem
        self.jorn = gl.jornGlob    #por enquanto, utiliza a jornada globalmente definida de 7h30min.
        self.viags = [idvx]        #aqui não precisa ser guardada a viagem, só precisa guardar o index
        self.almI = None
        self.almF = None

    ### BASE ######
    
    def sortV(self): self.viags.sort(key=lambda vx : gl.vdict['hi'][vx])

    ### DURAÇÕES ######    

    def hi(self):              #primeiro horario da primeira viagem alocada + tempo extra
        hList = [gl.vdict['hi'][vx] for vx in self.viags] #cria uma lista com todas as horas iniciais das viagens    
        if self.almI is not None: hList.append(self.almI)
        return min(hList)
    
    def hf(self):      #ultimo horario da ultima viagem alocada + tempo extra (quando add tempo extra cuidar aqui e na cabeJornada)
        hList = [gl.vdict['hf'][vx] for vx in self.viags]
        if self.almF is not None: hList.append(self.almF)
        return max(hList)
    
    def folgaI(self):
        if self.almI == None:
            return self.jornV()-self.condEf()
        else:
            return self.almI+self.jornV()-self.condEf()-self.almF
    
    def atribuiAlmoco(self): # almoço é testado aproximadamente no meio do serviço
        adicionou = False
        i=1
        while adicionou == False and i<len(self.viags): #se ja chegou mais ou menos no meio
            if gl.vdict['hf'][self.viags[i-1]]+gl.almGlob < gl.vdict['hi'][self.viags[i]]: #se não colide, coloca entre viagens
                self.almI = gl.vdict['hf'][self.viags[i-1]]
                self.almF = gl.vdict['hf'][self.viags[i-1]]+gl.almGlob
                adicionou = True
            i=i+1
            
        if adicionou == False and i == len(self.viags):
            if self.hf()<gl.meioTab:
                self.almI = gl.vdict['hf'][self.viags[i-1]]
                self.almF = gl.vdict['hf'][self.viags[i-1]]+gl.almGlob
                adicionou = True
            else:
                self.almF = gl.vdict['hi'][self.viags[0]]
                self.almI = gl.vdict['hi'][self.viags[0]] - gl.almGlob
                adicionou = True
            if adicionou == False: print("Problema ao atribuir almoço.")
                
               
        # almoço, horario inicial e final dele, não precisam estar lá na inicialzação do serviço
    
    def folgaE(self): return self.jorn - self.jornV()

    def condEf(self):          #calcula a condução efetiva - suponho que seja a soma de todas as durações de viagens
        durTotal = dtm.timedelta(0)
        for idvx in self.viags: durTotal = durTotal + gl.vdict['dur'][idvx]
        return durTotal

    def jornV(self): return self.hf()-self.hi()
    
    def horaPico(self): return sum([gl.vdict['pp'][vx] for vx in self.viags])*dtm.timedelta(hours = 6)

    ### VERIFICAÇÕES ######

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
    
    def colideAlmoco(self, vx):
        if self.almI>=gl.vdict['hi'][vx] and self.almI<gl.vdict['hf'][vx]:
            #logf.write("\n[Colidealmoço] Caso 1 - inicio da almoço está dentro da v1, mas v1 continua")
            return True #início da almoço está dentro da v1, mas v1 continua
        
        elif gl.vdict['hi'][vx]>=self.almI and gl.vdict['hi'][vx]<self.almF:
            #logf.write("\n[Colidealmoço] Caso 2 - inicio da v1 está dentro da almoço, mas almoço continua")
            return True #início da v1 está dentro da almoço, mas almoço continua
        
        elif gl.vdict['hi'][vx] == self.almI or gl.vdict['hf'][vx] == self.almF: #ambas coincidem em pelo menos um horário
            #logf.write("\n[Colidealmoço] Caso 3 - coincidem")
            #print(i, "| Viagens comparadas têm mesmo hi ou hf.")
            #if gl.vdict['ti'][vx] == gl.vdict['ti'][i2] or gl.vdict['tf'][vx] == gl.vdict['tf'][i2]: #as viagens são idênticas!!!
                #print(i, "| Viagens comparadas têm mesmo ti ou tf")
            return True 
        else: return False #viagens não colidem 
        
    def encaixaHorario(self, i1):
        colide = False
        for i2 in self.viags:
                #if gl.colideHorario(vx,vserv) == True: colide = colide + 1
            if gl.vdict['hi'][i2]>=gl.vdict['hi'][i1] and gl.vdict['hi'][i2]<gl.vdict['hf'][i1]:
                #logf.write("\n[ColideHorario] Caso 1 - inicio da v2 está dentro da v1, mas v1 continua")
                colide = True #início da v2 está dentro da v1, mas v1 continua
            
            elif gl.vdict['hi'][i1]>=gl.vdict['hi'][i2] and gl.vdict['hi'][i1]<gl.vdict['hf'][i2]:
                #logf.write("\n[ColideHorario] Caso 2 - inicio da v1 está dentro da v2, mas v2 continua")
                colide = True #início da v1 está dentro da v2, mas v2 continua
            
            elif gl.vdict['hi'][i1] == gl.vdict['hi'][i2] or gl.vdict['hf'][i1] == gl.vdict['hf'][i2]: #ambas coincidem em pelo menos um horário
                #logf.write("\n[ColideHorario] Caso 3 - coincidem")
                #print(i, "| Viagens comparadas têm mesmo hi ou hf.")
                #if vdict['ti'][i1] == vdict['ti'][i2] or vdict['tf'][i1] == vdict['tf'][i2]: #as viagens são idênticas!!!
                    #print(i, "| Viagens comparadas têm mesmo ti ou tf")
                colide = True 
        return not colide

    

        