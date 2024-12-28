import maya.cmds as cmd


def crea_cubo(scala):
    return cmd.polyCube(w=scala, h=scala, d=scala)[0]
    
def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1 
    
    return fib(n-1) + fib(n-2)
    

group_list = []
for i in range(0+1, 10+1):
    cubo_corrente = crea_cubo(i)
    print(cubo_corrente)
    cmd.setAttr(cubo_corrente + '.translateX', i*i)
    group_list.append(cubo_corrente)
    
fib_grp = cmd.group(group_list, n='cubi_sto_maledetto_fibonacci_grp')
