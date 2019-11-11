"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019
"""

import datetime as dtm
import classServico as sv
import variaveisGlobais as gl
import random as rd
import math
import copy

class Solucao:
    def __init__(self, servx):  #não tem como criar uma solução sem serviço
        gl.idsolGlob = gl.idsolGlob + 1 #adiciona ao contador global de soluções
        
        self.idsol = gl.idsolGlob #identifica a solução atual
        self.servs = {0: servx}  #inicializa dicionario de serviços e insere o primeiro
        self.viagSol = copy.deepcopy(servx.viags) #copia lista de viagens do serviço para usar na solução
        
    ### BASE ############         

    def sortV(self): self.viagSol.sort(key=lambda vx : gl.vdict['hi'][vx])
        
    def checaDuplicatas(self):
        self.sortV() #só por segurança
        for i in range(len(self.viagSol)-1):
            if self.viagSol[i] == self.viagSol[i+1]:
                gl.duplicatas = gl.duplicatas + 1
                
    

    ############## ADIÇÃO ################### 

    def addServ(self, servx):   #adiciona um novo serviço a essa solução
        self.servs.update({len(self.servs) : servx}) # guarda o serviço no dicionario servs
        self.viagSol.extend(copy.deepcopy(servx.viags))
        self.sortV() #coloca as viagens em ordem ascendente
    
    def encaixaVSol(self,vx):
        gl.logf.write("\n\n[encaixaVSol] Viagem "+str(vx)+ " | hi = "+str( gl.vdict['hi'][vx])+" | hf = "+str( gl.vdict['hf'][vx])+" | ti = "+str( gl.vdict['ti'][vx])+" | tf = "+str( gl.vdict['tf'][vx]))
        adicionou = False
        j = 0 #para percorrer cada serviço da solução
        while adicionou == False and j<len(self.servs): # percorre cada serviço da solução até chegar ao fim da lista de serviços
            #só encerra quando conseguir adicionar viagem (adicionou = 1)
            #gl.logf.write("\n[encaixaVSol] Testa se a Viagem "+str(vx)+ " cabe no serviço "+str(j)+" pelas funções cabeJornada e encaixaTerminal")
            if self.servs[j].cabeJornada(vx) and self.servs[j].encaixaTerminal(vx): # cabe na jornada? CABE
                """adicionar aqui as condições de Terminal e de Almoço"""
                colide = 0 # percorrer todas as viagens do serviço atual da solução e ver se não colide
                #print("Colide ", colide)
                #gl.logf.write("\n[encaixaVSol] Testa se a Viagem "+str(vx)+ " cabe no serviço "+str( j)+" pela verificação de colisão com as viagens")
                for vserv in self.servs[j].viags:
                    if gl.colideHorario(vx,vserv) == True:
                        #gl.logf.write("\n[encaixaVSol] A viagem "+ str(vx) + " colidiu com a viagem " +str(vserv)+ " no serviço "+str(j))
                        colide = colide + 1
                if colide == 0:

                    gl.logf.write("\n[encaixaVSol] A Viagem "+str(vx)+ " não colidiu com nenhuma viagem e atendeu aos outros três requisitos, portanto será adicionada no serviço "+str( j))
                    
                    self.servs[j].viags.append(vx)
                    self.servs[j].sortV()

                    self.viagSol.append(vx)
                    self.sortV()

                    adicionou = True

                    #print("- VIAGEM ADICIONADA em serviço existente")
                    #print("Serviço n° ", j, " na lista, idserv global = ", self.servs[j].ids,", advinda de mutação")
                    #print("")
            j = j + 1
            #print("Fim do while -> j + 1 = ", j)
            if j == len(self.servs) and adicionou == False: #se chegou ao final da lista de serviços sem ter adicionado
                adicionou = True
                gl.logf.write("\n[encaixaVSol] A Viagem "+str(vx)+ " não coube em nenhum serviço portanto será criado um novo serviço")
                self.addServ(sv.Servico(vx))
        return adicionou

    def viagNovaRandom(self): # função que retorna uma viagem aleatória do vdict, mas apenas se ela já não existir na solução.
        if len(self.viagSol)<len(gl.vdict['hi']):
            notInSol = [vx for vx in gl.vdict['hi'] if vx not in self.viagSol]
            return notInSol[rd.randrange(len(notInSol))]
        else: 
            gl.popCompl.addSol(self.geraCopia()) #é adicionada uma cópia aqui, que vai ficar intocada.
            print("Uma solução completa foi atingida. Cópia armazenada em popCompl.")
            return False

    ############ CÓPIA ######################

    def prsol(self):
        print ("")
        print("FUNÇÃO PRINT SOLUÇÃO ---------------------------")
        print("SOLUÇÃO idSol %3d  | %3d serviços  | %3d viagens:" %(self.idsol,len(self.servs),len(self.viagSol)))
        print("viagSol", self.viagSol)
        print ("")
        #print("Solução ", self.idsol, "| ", len(self.servs), " serviços | ", len(self.viagSol), " viagens")
        for i in range(len(self.servs)):
            print("%3d  Serviço %3d -------------------------------" %(i, self.servs[i].ids))
            #print(i, "Serviço", self.servs[i].ids, " - ", self.servs[i].viags, "----------------------------------------")
            for j in range(len(self.servs[i].viags)):
                print("%3d  Viagem %3d  =  %2d:%2d-%2d:%2d  -  Term Inic %2d" %(j,self.servs[i].viags[j],gl.vdict['hi'][self.servs[i].viags[j]].hour,gl.vdict['hi'][self.servs[i].viags[j]].minute,gl.vdict['hf'][self.servs[i].viags[j]].hour,gl.vdict['hf'][self.servs[i].viags[j]].minute,gl.vdict['ti'][self.servs[i].viags[j]]))
                #print(j, "Viagem", self.servs[i].viags[j], " - hi ", gl.vdict['hi'][self.servs[i].viags[j]].hour, "h", gl.vdict['hi'][self.servs[i].viags[j]].minute, "min - hf", gl.vdict['hf'][self.servs[i].viags[j]].hour,"h",  gl.vdict['hf'][self.servs[i].viags[j]].minute, "min - ti", gl.vdict['ti'][self.servs[i].viags[j]])
        print ("")
        
        
    def geraCopia(self):
        
        serv0filho = sv.Servico(0)
        serv0filho.viags = copy.deepcopy(self.servs[0].viags)
        serv0filho.sortV()
        filho = Solucao(serv0filho)
                
        for jserv in range(1,len(self.servs)):
            servxfilho = sv.Servico(0)
            servxfilho.viags = copy.deepcopy(self.servs[jserv].viags)
            servxfilho.sortV()
            filho.addServ(servxfilho)
            
        return filho
          
    ############# GENÉTICOS #################
    
    def cruza(self, viagSolPai2): #cruza duas soluções. gera um filho. entra a solução base e as viagens da solução a adicionar
        filho = self.geraCopia()
        for vx in viagSolPai2: # percorre cada viagem de nova
            if vx not in filho.viagSol: # essa viagem já está na solução filho? NÃO ESTÁ:
                adicionou = filho.encaixaVSol(vx)
                if adicionou == False: print("ERRO ESTRANHÍSSIMO AO ENCAIXAR VIAGEM NA SOLUÇÃO")
        return filho
    
    def muta(self):            #realiza mutação na solução atual. a aleatoriedade está fora dessa função, no bloco do código.
        filho = self.geraCopia()
        vx = filho.viagNovaRandom()
        # a diferença para o cruzamento é que aqui ele vai forçar que entre alguma viagem nova.
        # no cruzamento ele só tenta a que vem de Pai2. se já tem, só PASS.
        adicionou = filho.encaixaVSol(vx)
        if adicionou == False: print("ERRO ESTRANHÍSSIMO AO ENCAIXAR VIAGEM NA SOLUÇÃO")
        return filho

    def custog(self): #custo g - custo da solução atual/existente
        fin = dtm.timedelta(0) # folga interna
        fex = dtm.timedelta(0) # folga externa
        jorns = dtm.timedelta(0) 
        for servx in self.servs: # custo das folgas & custo dos n serviços
            fin = fin + self.servs[servx].hf() - self.servs[servx].hi() - self.servs[servx].condEf()
            fex = fex + self.servs[servx].jorn + self.servs[servx].hi() - self.servs[servx].hf()
            jorns = jorns + self.servs[servx].jorn             
        """custo dos horarios de pico - FAZER DEPOIS"""
        return gl.tau*fin + fex + gl.alfa*jorns
    
    def custoh(self): #custo h - penalidade relativa a "quanto falta para atingir uma suposta solução ótima"
        #serviços faltantes = sf = arredonda para numero inteiro
        sf = math.ceil((len(gl.vdict['hi']) - len(self.viagSol)) / gl.viagsPorServ)
        # HR = Folga Restante = sf * hmus
        # Serviços restantes = sf * alfa
        # precisei multiplicar pela jornada pra poder fazer a adição
        return sf * gl.hmus + sf * gl.alfa * gl.jornGlob
        
    def custo(self): return self.custog() + self.custoh()*gl.gama           #determina o custo da solução atual de acordo com a tese de Elizondo