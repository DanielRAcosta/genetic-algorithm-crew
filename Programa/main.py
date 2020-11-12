"""
Definição de Escala de Tripulação de Transporte Coletivo Utilizando Algoritmo Genético
Daniel Rodrigues Acosta
Universidade Federal do Rio Grande do Sul
Junho/2019

Main - Execução do Algoritmo Principal
"""

import programa as prog

# modo de execução em série
#for iExec in range(65,70): prog.prog(iExec)

# modo de execução única
#prog.prog(70)

# pegar novamente as antigas
pops = {10: prog.gl.inpop('10exec'), 20: prog.gl.inpop('20exec')} 
chav = {}
for px in pops:
    chav.update({px:list(pops[px].sols.keys())})

solExemplo = pops[20].sols[460935]
    
"""
for p1 in pops:
    outras = list(pops.keys())
    outras.remove(p1)
    for sol1 in pops[p1].sols:
        for p2 in outras:
            for sol2 in pops[p2].sols:
                if pops[p1].sols[sol1].custog() == pops[p2].sols[sol2].custog(): custo_igual = True
                else: custo_igual = False
                
                #if custo_igual == True: serv_igual = checa_serv(sol1,sol2)
                #else: serv_igual = False
                
                print(p1,sol1,p2,sol2,custo_igual)#,serv_igual)
"""  
"""
for px in pops:
    for sx in pops[px].sols:
        print(px, sx, pops[px].sols[sx].custog())
"""