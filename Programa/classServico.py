"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""

import variaveisGlobais as gl

import datetime as dtm

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
    
    def folgaE(self): return self.jorn - self.jornV() - gl.intervPontaGlob*2

    def condEf(self):          #calcula a condução efetiva - suponho que seja a soma de todas as durações de viagens
        durTotal = dtm.timedelta(0)
        for idvx in self.viags: durTotal = durTotal + gl.vdict['dur'][idvx]
        return durTotal

    def jornV(self): return self.hf()-self.hi()
    
    def jornI(self): return self.hi() + self.jornV()/2 - self.jorn/2 # Inicio da jornada apenas para visualizar no Gantt, centralizada
    
    def jornF(self): return self.jornI() + self.jorn # Fim da jornada apenas para visualizar no Gantt, centralizada
    
    def horaPico(self): return sum([gl.vdict['pp'][vx] for vx in self.viags])*dtm.timedelta(hours = 6)

    ### VERIFICAÇÕES ######

    def cabeJornada(self,idvx): #checa se para realizar a viagem desejada, a jornada máxima não seria estourada

        if gl.vdict['hi'][idvx]>self.hf(): #caso 1 - viagem nova no final do serviço
            if gl.vdict['hf'][idvx]-self.hi() < self.jorn - gl.intervPontaGlob*2 : return True # CABE se mesmo colocando ela, não ultrapassa a jornada
            else: return False # NAO CABE - ultrapassou               
            
        elif gl.vdict['hf'][idvx]<self.hi(): #caso 2 - viagem nova no inicio do serviço
            if self.hf()-gl.vdict['hi'][idvx] < self.jorn - gl.intervPontaGlob*2 : return True # CABE
            else: return False # NAO CABE
            
        elif gl.vdict['hi'][idvx]>self.hi() and gl.vdict['hf'][idvx]<self.hf(): return True # caso 3 - viagem nova dentro do serviço - não altera duração total
        else: return False # pela lógica, a nova viagem está colidindo (tem interseção) com a última do serviço.
                
    def encaixaTerminal(self, idvx): #verifica se os terminais da viagem encaixam no serviço
        i_hs = [idv for idv in self.viags if gl.vdict['hf'][idv] < gl.vdict['hi'][idvx]]
        hs = [gl.vdict['hf'][idv] for idv in self.viags if gl.vdict['hf'][idv] < gl.vdict['hi'][idvx]]
        try: # caso a lista dê vazia
            anterior = i_hs[hs.index(max(hs))]
            if gl.vdict['hf'][anterior]<=gl.vdict['hi'][idvx] and gl.vdict['tf'][anterior]==gl.vdict['ti'][idvx]:
                encaixa_ant = True
            else: encaixa_ant = False 
        except: encaixa_ant = True
            
        i_hs = [idv for idv in self.viags if gl.vdict['hi'][idv] > gl.vdict['hf'][idvx]]
        hs = [gl.vdict['hi'][idv] for idv in self.viags if gl.vdict['hi'][idv] > gl.vdict['hf'][idvx]]
        try: # caso a lista dê vazia
            posterior = i_hs[hs.index(min(hs))]
            if gl.vdict['hf'][idvx]<=gl.vdict['hi'][posterior] and gl.vdict['tf'][idvx]==gl.vdict['ti'][posterior]:
                encaixa_post = True
            else: encaixa_post = False 
        except: encaixa_post = True
        return encaixa_ant and encaixa_post   
    
    def colideAlmoco(self, vx):
        if (self.almI != None) and (self.almF != None):
            if self.almI>=gl.vdict['hi'][vx] and self.almI<gl.vdict['hf'][vx]: return True #início da almoço está dentro da v1, mas v1 continua
            elif gl.vdict['hi'][vx]>=self.almI and gl.vdict['hi'][vx]<self.almF: return True #início da v1 está dentro da almoço, mas almoço continua
            elif gl.vdict['hi'][vx] == self.almI or gl.vdict['hf'][vx] == self.almF: return True #ambas coincidem em pelo menos um horário  
            else: return False #viagens não colidem
        else: return False # não colidem porque ainda não tem almoço
    
    def encaixaHorario(self, hi1, hf1): #input gl.vdict['hi'][i1], gl.vdict['hf'][i1]
        colide = False
        for i2 in self.viags:    
            if gl.vdict['hi'][i2]>=hi1 and gl.vdict['hi'][i2]<hf1: colide = True #início da v2 está dentro da v1, mas v1 continua
            elif hi1>=gl.vdict['hi'][i2] and hi1<gl.vdict['hf'][i2]: colide = True #início da v1 está dentro da v2, mas v2 continua            
            elif hi1 == gl.vdict['hi'][i2] or hf1 == gl.vdict['hf'][i2]: colide = True #ambas coincidem em pelo menos um horário
        return not colide
    
    def tentaAtribuirAlmoco(self): # almoço é testado aproximadamente no meio do serviço
        adicionou = False
        
        # tenta adicionar bem no meio - vê se cabe no tempo e se colide com viagens
        if self.hf() - self.hi() - self.condEf() > gl.almGlob:
            meioServ = self.hi() + (self.hf()-self.hi())/2
            """TENTATIVA 1 - BEM NO MEIO DO SERVIÇO"""
            if self.encaixaHorario(meioServ - gl.almGlob/2,meioServ + gl.almGlob/2): # if folga I > almGlob (só que abri a conta pra simplificar)
                self.almI = meioServ - gl.almGlob/2
                self.almF = meioServ + gl.almGlob/2
                adicionou = True
            else: #sei que tem espaço mas não bem no meio... vai ter que ir vendo os espaços
                """TENTATIVA 2 - NO MEIO MAS NÃO EXATAMENTE"""
                #mapeia espaços vazios internos
                #supondo que ta na ordem... primeiro pega as viagens
                hiFolgasList = [gl.vdict['hf'][idv] for idv in self.viags]
                hfFolgasList = [gl.vdict['hi'][idv] for idv in self.viags]
                
                #hi da primeira folga = hf da primeira viagem, e assim por diante
                hiFolgasList = hiFolgasList[:-1] #exclui ultimo
                #hf da primeira folga = hi da segunda viagem, e assim por diante
                hfFolgasList = hfFolgasList[1:] #exclui primeiro
                
                #calcula duração folgas
                durFolgasList=[]
                deletaItemList=[]
                for i in range(len(hiFolgasList)):
                    durFolgasList.append(hfFolgasList[i] - hiFolgasList[i])
                    if durFolgasList[i]<gl.almGlob: deletaItemList.append(i) #guarda index para deletar depois todas as que nao cabem
                
                #deleta as que não cabem
                if len(deletaItemList) < len(durFolgasList): #só se tiver alguma que cabe
                    
                    i = len(deletaItemList)-1 
                    while i >= 0 :
                        hiFolgasList.pop(deletaItemList[i])
                        hfFolgasList.pop(deletaItemList[i])
                        durFolgasList.pop(deletaItemList[i])
                        i -= 1
                        
                    #ordenar por mais proximos do meio
                    distanciaAteMeio = []
                    antesMeio=[]
                    for hi in hiFolgasList: #dois casos pra que nao haja delta negativo
                        if hi<meioServ and hfFolgasList[hiFolgasList.index(hi)]<meioServ:
                                distanciaAteMeio.append(meioServ-hfFolgasList[hiFolgasList.index(hi)])
                                antesMeio.append(True)
                        else:
                            distanciaAteMeio.append(hi-meioServ)
                            antesMeio.append(False)
                        
                    indices_ordenados = []
                    for i in range(len(distanciaAteMeio)): indices_ordenados.append((i,antesMeio[i]))
                    indices_ordenados.sort(key= lambda indice: distanciaAteMeio[indice[0]])
                    indice_mais_proxima = indices_ordenados[0] #pegar so a mais proxima que cabe
                        
                    if indice_mais_proxima[1]:
                        self.almF = hfFolgasList[indice_mais_proxima[0]]
                        self.almI = self.almF - gl.almGlob
                    else:
                        self.almI = hiFolgasList[indice_mais_proxima[0]]
                        self.almF = self.almI + gl.almGlob
                    
                    adicionou = True
                    
                    # ver se atende às horas min e max de almoço... só se jornV() eh grande o bastante
                    """faltou"""
        if not adicionou:
            """TENTATIVA 3 """
            if self.hi()>gl.meioTab-dtm.timedelta(hours=1) and self.jornV()>dtm.timedelta(hours=1)+gl.intervPontaGlob and gl.almGlob<=gl.jornGlob-gl.intervPontaGlob-self.jornV()-dtm.timedelta(hours=2.5): #começa muito tarde... põe antes
                self.almF = self.hi()
                self.almI = self.almF - gl.almGlob
                adicionou = True
            else: #começa cedo, põe depois
                self.almI = self.hf()
                self.almF = self.almI + gl.almGlob
                adicionou = True
        return adicionou
    
    def encaixaViagAlmoco(self, vx): #retorna True ou False se dá pra empurrar o almoço pro lado e mesmo assim alocar a viagem.
        hf_anteriores = [gl.vdict['hf'][idv] for idv in self.viags if gl.vdict['hf'][idv] < self.almI]
        hi_posteriores = [gl.vdict['hi'][idv] for idv in self.viags if gl.vdict['hi'][idv] > self.almF]
        try:
            inicFolga = hf_anteriores.sort(reverse=True)[0]
            fimFolga = hi_posteriores.sort()        
            
            if gl.almGlob + dtm.timedelta(minutes = 5) <= fimFolga-gl.vdict['hf'][vx]: # cabe depois
                self.almI = gl.vdict['hf'][vx] + dtm.timedelta(minutes = 2)
                self.almF = self.almI + gl.almGlob
                return True
            elif gl.almGlob  + dtm.timedelta(minutes = 5) <= gl.vdict['hi'][vx] - inicFolga: # cabe antes
                self.almF = gl.vdict['hf'][vx] - dtm.timedelta(minutes = 2)
                self.almI = self.almF - gl.almGlob
                return True
            else: return False
        except: return False
        
        """se der True, alteração do almoço deve ser feita aqui e a da viagem fora"""
    