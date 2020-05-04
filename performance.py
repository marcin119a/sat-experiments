import os
import tensorflow as tf
import itertools
from neuralheuristicsforsat.helpers import chunkIt, save_to_csv

def predict(params):
    complexity = 300
    tfrecord_location = '/content/neuralheuristicsforsat/sr_{0}'.format(complexity)
    name = "train_21021_sr_{0}.tfrecord".format(complexity)
    filename = os.path.join(tfrecord_location, name)

    record_iterator = tf.python_io.tf_record_iterator(path=filename)
    preds = []
    # targes = []
    batch_size = 300
    n = 300

    train_set = {'cnf': list(), 'sat': list()}
    sim_results = list()

    for string_record in itertools.islice(record_iterator, batch_size):
        example = tf.train.Example()
        example.ParseFromString(string_record)

        m = len(example.features.feature["inputs"].float_list.value) // 2

        inputs = chunkIt(example.features.feature["inputs"].float_list.value,
                         m)  # split examp: [0,1,2,3,4,5] into [0,1], [2,3], [4,5]

        train_set['cnf'].append(inputs)
        targ = int(example.features.feature["sat"].float_list.value[0])
        train_set['sat'].append(targ)

        start = time.time()
        sim_result = SIMCim(params, n, m,
                            inputs)  # predict SIMCim, inputs- params ISING Model, n- variables, M-clausures

        end = time.time()

        save_to_csv('logs_', [[m, m / n, sim_result, targ, end - start]], n)

        sim_results.append(sim_result)

    return (sim_results, train_set)
