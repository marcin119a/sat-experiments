import numpy as np
import random 
import csv 
import time


def ising_params(m, n, matrix):
    """ Encoding SAT matrix to Ising 2-body Hamiltonian folowing
        S.Santra et al. Max 2-SAT with up to 108 qubits (2014)."""

    v = matrix

    # constructing Ising matrix and biases
    J = np.zeros((n, n), dtype=np.float32)
    h = np.zeros(n, dtype=np.float32)
    # the local fields

    for j in range(m):
        index1 = -1
        index2 = 0
        for i in range(n):
            if v[j, i] != 0 and index1 == -1:
                index1 = i + 1
                continue
            if v[j, i] != 0 and index1 != 0:
                index2 = i + 1
                break
        J[index1 - 1, index2 - 1] += v[j, index1 - 1] * v[j, index2 - 1]
        h[index1 - 1] += -v[j, index1 - 1]
        h[index2 - 1] += -v[j, index2 - 1]
    return J, h

def generate_pycosat(n_variables, n_clauses, k_var):
    """
       Generates k_var-SAT problem in cnf-format
    """
    a = list(range(-n_variables, 0)) + list(range(1, n_variables + 1))
    b = [0 for _ in range(n_clauses)]
    current_clause_num = 0
    while current_clause_num < n_clauses:
        clause = []
        while True:
            var = random.choice(a)
            if var not in clause and -var not in clause:
                clause.append(var)
            if len(clause) == k_var:
                break
        if clause not in b:
            b[current_clause_num] = clause
            current_clause_num += 1
    return b


def data_to_matrix(m, n, data):
    matrix = np.zeros((m, n), dtype=np.int32)
    for j in range(m):
        var1, var2 = data[j][0], data[j][1]
        matrix[j][abs(var1) - 1] = var1 // abs(var1)
        matrix[j][abs(var2) - 1] = var2 // abs(var2)
    return matrix


def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(list(map(int, seq[int(last):int(last + avg)])))
        last += avg

    return out


def save_to_csv(file_name, data, n):
  logs = open("logs_{0}_{1}.csv".format(file_name, n, time.strftime("%Y%m%d")), 'a')
  with logs:
     writer = csv.writer(logs)
     writer.writerows(data)