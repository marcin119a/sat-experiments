import itertools
import os
import tensorflow as tf
from neuralheuristicsforsat.helpers import chunkIt, save_to_csv

from sklearn.metrics import mean_absolute_error, mean_squared_error

import time
from hyperopt import fmin, Trials, rand, tpe, STATUS_OK

from timeit import default_timer as timer
import numpy as np
from SIMCIM import SIMCim

global ITERATION


ITERATION = 0

def objective(params):
    # Keep track of evals
    global ITERATION
    n = 100

    ITERATION += 1

    start = timer()

    y_pred, train_set = predict(params)

    run_time = timer() - start

    # todo implemented seed
    if params['loss'] == "mean_squared_error":
      loss = np.square(np.subtract(train_set['sat'], y_pred)).mean()
    else:
      loss = mean_absolute_error(train_set['sat'], y_pred)

    save_to_csv('gbm_trials_', [[loss, params, ITERATION, run_time]], n)

    return {'loss': loss, 'params': params, 'iteration': ITERATION,
            'train_time': run_time, 'status': STATUS_OK}


def predict(params):
    n = params['complexity'] #no. of variables
    tfrecord_location = 'sr_{0}'.format(n)
    name = "train_{1}_sr_{0}.tfrecord".format(n, params['seed'])
    filename = os.path.join(tfrecord_location, name)

    record_iterator = tf.python_io.tf_record_iterator(path=filename)
    preds = []
    batch_size = params['observations']

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
