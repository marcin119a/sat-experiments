import ast
from utilities import save_to_csv

def pegasus_phase_draw(energies_file, test_set_file, n):

    with open(energies_file, "r") as intput:
        energies = eval(intput.read())


    with open(test_set_file, "r") as inf:
        dict_from_file = eval(inf.read())


    for energy, cnf , sat in zip(energies, dict_from_file['cnf'], dict_from_file['sat']):
        m = len(cnf)
    
        if m + energy == 0:
            en = 1 
        else: 
            en = 0

        save_to_csv('max_sat_', [[m, m / n, en , sat]], n)


    import pandas as pd
    import numpy as np 
    import matplotlib.pyplot as plt


    df = pd.read_csv('logs_max_sat__{0}.csv'.format(n), names=['M','alfa','y_hat','y_acc'], sep=',').sort_values(['alfa'])[0:1000]



    bins = np.arange(0, 2.1, 0.20)

    df['bins'] = pd.cut(df.alfa, bins) 


    ss_acc = df.groupby('bins')['y_acc'].agg(['sum', 'count'])
    ss_hat = df.groupby('bins')['y_hat'].agg(['sum', 'count'])



    y = [x.mid for x in ss_acc.index.values]


    plt.title('2-SAT, each point is averaged by step: (1/20)', fontsize=14)
    plt.plot(y, ss_hat['sum']/ss_hat['count'], "-",label='Pegasus-{0}'.format(n))
    plt.plot(y, ss_acc['sum']/ss_acc['count'], "-",label='MiniSAT-{0}'.format(n))



    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
    plt.grid()
    plt.legend(fontsize=12)
    plt.show()
    plt.savefig('phase{0}'.format(n))
    plt.close()

    