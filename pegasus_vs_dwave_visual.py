from pegasus_vs_2000 import pegasus_phase_draw
from pegasus_vs_2000 import save_datas
n = 100
save_datas('r_pegasus/0/sr_{0}/params/list_out_energy'.format(n), 'r_dwave/0/sr_{0}/params/list_out_energy'.format(n), 'r_pegasus/0/sr_{0}/params/test_set'.format(n), n)
pegasus_phase_draw('r_pegasus/0/sr_{0}/params/list_out_energy'.format(n), 'r_dwave/0/sr_{0}/params/list_out_energy'.format(n) ,'r_pegasus/0/sr_{0}/params/test_set'.format(n), n)