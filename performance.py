import os
import tensorflow as tf
import itertools
from neuralheuristicsforsat.helpers import chunkIt, save_to_csv
import time
from SIMCIM import SIMCim

def predict(params):
    n = params['complexity']
    tfrecord_location = '/content/sat-experiments/sr_{0}'.format(n)
    name = "train_{1}_sr_{0}.tfrecord".format(n, params['seed'])
    filename = os.path.join(tfrecord_location, name)

    record_iterator = tf.python_io.tf_record_iterator(path=filename)
    preds = []
    # targes = []
    batch_size = params['observations']

    train_set = {'cnf': list(), 'sat': list()}
    sim_results = list()

    for string_record in itertools.islice(record_iterator, batch_size):
        example = tf.train.Example()
        example.ParseFromString(string_record)

        m = len(example.features.feature["inputs"].float_list.value) // 2

        inputs = chunkIt(example.features.feature["inputs"].float_list.value, m) 
        train_set['cnf'].append(inputs)
        targ = int(example.features.feature["sat"].float_list.value[0])
        train_set['sat'].append(targ)

        start = time.time()
        sim_result = SIMCim(params, n, m, inputs)  # predict SIMCim, inputs- params ISING Model, n- variables, M-clausures

        end = time.time()

        save_to_csv('logs_', [[m, m / n, sim_result, targ, end - start]], n)

        sim_results.append(sim_result)

    return (sim_results, train_set)
