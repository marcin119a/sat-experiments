import itertools

def brute_force_2_max_sat(cnf):
    literals = set()
    m = 0
    cnf_max = []
    for conj in cnf:
        for disj in conj:
            literals.add(disj[0])
 
    literals = list(literals)
    n = len(literals)
    for seq in itertools.product([True,False], repeat=n):
        a = set(zip(literals, seq))
        check_cnf = [bool(disj.intersection(a)) for disj in cnf]
        
        if m < check_cnf.count(True):
          m = check_cnf.count(True)
          cnf_max = check_cnf
        if all(check_cnf):
            return True, len(cnf)
 
    return cnf_max, m

"""
Transformation from list format into dictonary format. 
from [[1,-2], [2,3]] -> {('0000000001', True), ('0000000002', False), ('0000000002', True), ('0000000003', True)}

"""
def transform(lista):
  result = []
  for cnf in lista:
    conj = set()
    for omega in cnf:
      index = abs(omega)
      neg = (omega > 0)
      conj.add((str(index).rjust(10, '0'), neg ))
    result.append(conj)
  return result


"""
dump into akmaxsat format
Example:
p cnf 4 20
4 -1 0
-17 6 0
-19 -1 0
1 -1 0
    Parameters
    ----------
    input_list : list of 2D lists
        example: [[0,1], [1,0]]
     m: int
        number of clauses
     n: int
        number of variables
     name: string
        name for file
"""

def dump(input_list, n, m, name):
  f = open("{0}.txt".format(name),"a+")    
  f.write("p cnf %d %d\n" % (2*n, m))
  for x in input_list:
    a = x[0]
    b = x[1]
    f.write("%d %d %d\n" % (a, b, 0))
  f.close()


"""
From out of akmaxsat format like: 
"14 -4 -20"
into 
{('0000000014', True), ('0000000004', False), ('0000000020', False)}
    Parameters
    ----------
    assigment : string 
        assigment returned by akmaxsat
"""

def function_from_akmaxsat(assigment):
  out = [int(x) for x in assigment.split(" ")]
  conj = set()
  for x in out:
      conj.add((
        str(abs(x)).rjust(10, '0'),
        bool(x > 0),
      ))
  return conj
"""
    from input of akmaxsat to list. 
    Parameters
    ----------
    file: string
        path to file-formated cnf
"""
def akmaxsat_format_to_list(file):
  
  literals = set()
  f = open(file, "r")
  cnf_str = f.read().split("\n")
  m = int(cnf_str[0].split(" ")[2])
  n = int(cnf_str[0].split(" ")[3])
  cnf_str = cnf_str[1:m+1]
  input = [[int(x.split(" ")[0]), int(x.split(" ")[1])] for x in cnf_str]

  return m,n,input

"""
run akmaxsat binary algorithm
    Parameters
    ----------
    file : string
        src binary file
    input: string
        path to file-formated cnf
"""
ASSIGMENT = 8
def akmaxsat_run(file, input):
  import subprocess
  output = str(subprocess.check_output([file, input])).split("\\n")
  vart_max = function_from_akmaxsat(output[ASSIGMENT].replace("v ", ""))

  return vart_max


