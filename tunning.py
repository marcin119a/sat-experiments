import itertools
import os
import tensorflow as tf
from helpers import chunkIt, save_to_csv
import time
from hyperopt import fmin, Trials, rand, tpe, STATUS_OK

from timeit import default_timer as timer
import numpy as np


def objective(params):
    # Keep track of evals
    global ITERATION
    n = 100

    ITERATION += 1

    start = timer()

    y_pred, train_set = predict(params)

    run_time = timer() - start

    # todo implemented seed
    loss = np.square(np.subtract(train_set['sat'], y_pred)).mean()

    save_to_csv('gbm_trials_', [[loss, params, ITERATION, run_time]], n)

    return {'loss': loss, 'params': params, 'iteration': ITERATION,
            'train_time': run_time, 'status': STATUS_OK}


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



tpe_trials = Trials()
rand_trials = Trials()

global  ITERATION

ITERATION = 0

# Create the algorithms
tpe_algo = tpe.suggest
rand_algo = rand.suggest

rand_best = fmin(fn=objective, space=space, algo=rand_algo, trials=rand_trials,
                 max_evals=2000)