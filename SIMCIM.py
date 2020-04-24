import numpy as np
import random
import torch
import matplotlib.pyplot as plt
from tqdm import trange

# use GPU to speed up SimCIM 
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')


def data_to_matrix(m, n, data):
    matrix = np.zeros((m, n), dtype=np.int32)
    for j in range(m):
        var1, var2 = data[j][0], data[j][1]
        matrix[j][abs(var1)-1] = var1//abs(var1)
        matrix[j][abs(var2)-1] = var2//abs(var2)
    return matrix


def ising_params(m, n, matrix):
    
    """ Encoding SAT matrix to Ising 2-body Hamiltonian folowing 
        S.Santra et al. Max 2-SAT with up to 108 qubits (2014).""" 
    
    v = np.zeros((m, n),dtype=np.int32)
    for i in range(m):
        expr = matrix[i]
        for index, k in enumerate(expr):
            if k!=0: v[i,index] = k//abs(k) 
                
    # constructing Ising matrix and biases
    J = np.zeros((n, n), dtype=np.float32)
    h = np.zeros(n,dtype=np.float32)
    
    for j in range(m):
        index1 = -1
        index2 = 0
        for i in range(n):
            if v[j,i]!=0 and index1==-1:
                index1 = i+1
                continue
            if v[j,i]!=0 and index1!=0: 
                index2 = i+1
                break
        J[index1-1,index2-1] += v[j,index1-1]*v[j,index2-1]
        h[index1-1] += -v[j,index1-1] 
        h[index2-1] += -v[j,index2-1]  
    return J, h


def ampl_inc(J, b, c, zeta, p, sigma, attempt_num, dt):
    """
    Increments and initializes spins
    """
    return (p*c + zeta*(2*torch.mm(J, c) + b))*dt +\
                     (sigma*torch.zeros((c.size(0), attempt_num), dtype=torch.float32, device=device))*dt


def init_ampl(dim, attempt_num):
    
    return torch.randn((dim, attempt_num), dtype=torch.float32)


def energy_calculation(J, b, step1, dt, sigma, alpha, zeta, offset, dim, attempt_num, N, c_th, m):
    """ 
    Calculates Ising energy according to 
    S.Santra et al. Max 2-SAT with up to 108 qubits (2014). and
    SimCIM annealer from 
    E. S. Tiunov et al. Annealing by simulating the coherent Ising machine (2019).
    Here is used linear pump function.
    """
    N = int(N)
    attempt_num = int(attempt_num)
    c_current = init_ampl(dim, attempt_num).to(device) 
    dc_momentum = torch.zeros((dim, attempt_num),dtype=torch.float32,device=device)
    init_lambda = np.array([offset + step1*i/float(N) for i in range(N)])
    
    for i in range(1, N):
        dc = ampl_inc(J, b, c_current, zeta, init_lambda[i], sigma, attempt_num, dt)
        dc_momentum = alpha*dc_momentum + (1-alpha)*dc
        dc_momentum /= (1.-alpha**i)
        c1 = c_current + dc_momentum
        th_test = (torch.abs(c1)<c_th).type(torch.float32)
        c_current = c_current + th_test*dc_momentum
        spins_current = torch.sign(c_current)
        
    return (torch.einsum('ij,ik,jk->k', (J, spins_current, spins_current)) +
            torch.einsum('ij,ik->k', (b, spins_current)))*0.25 - 0.25*m
# initial params + hyperparameters


def SIMCim(params, n, m, input_2cnf):
    c_th = 1.

    matrix = data_to_matrix(m, n, input_2cnf)
    J, h = ising_params(m, n, matrix)
    lambda_max = abs(np.max(np.linalg.eigvals(-J)))
    J = torch.tensor(-J, dtype=torch.float32, device=device)
    b = torch.tensor(-h, dtype=torch.float32, device=device).unsqueeze(1)
    value = torch.max(
        energy_calculation(J, b, lambda_max, params['dt'], params['sigma'], params['alpha'], params['zeta'],
                           -lambda_max, J.size(0), params['attempt_num'], params['N'], c_th, m))
    satis_simcim = int(value.cpu().numpy() == 0)  # checking satisfactory

    return satis_simcim


