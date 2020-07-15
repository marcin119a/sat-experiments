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

def dump(input_list, m, n):
  f = open("a{0}.txt".format(m),"a+")    
  f.write("p cnf %d %d\n" % (len(input_list), n))
  for x in input_list:
    a = x[0]
    b = x[1]
    f.write("%d %d %d\n" % (a, b, 0))
  f.close()

def function_from_akmaxsat(out):
  conj = set()
  for x in out:
      conj.add((
        str(abs(x)).rjust(10, '0'),
        bool(x > 0),
      ))
  return conj
