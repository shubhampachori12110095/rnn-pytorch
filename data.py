# -*- coding: utf-8 -*-
#pylint: skip-file
import sys
import os
import numpy as np
import cPickle, gzip
from random import shuffle

curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))

def char_sequence(f_path = None, batch_size = 1):
    seqs = []
    i2w = {}
    w2i = {}
    lines = []
    if f_path == None:
        f = open(curr_path + "/data/toy.txt", "r")
    else:
        f = open(curr_path + "/" + f_path, "r")
    for line in f:
        line = line.strip('\n').lower()
        if len(line) < 3:
            continue
        lines.append(line)
        for char in line:
            if char not in w2i:
                i2w[len(w2i)] = char
                w2i[char] = len(w2i)
    f.close()

    for i in range(0, len(lines)):
        line = lines[i]
        x = np.zeros((len(line), 1))
        for j in range(0, len(line)):
            x[j,] = w2i[line[j]]
        seqs.append(x)

    data_xy = batched(len(seqs), batch_size)
    print "#dic = " + str(len(w2i))
    return seqs, i2w, w2i, data_xy

def batched(x_size, batch_size):
    ids = [i for i in xrange(x_size)]
    shuffle(ids)
    batch_list = []
    batch_ids = []
    for i in xrange(x_size):
        idx = ids[i]
        batch_ids.append(idx)
        if len(batch_ids) == batch_size or i == (x_size - 1):
            batch_list.append(batch_ids)
            batch_ids = []
    return batch_list

class BatchData:
    def __init__(self, flist, len_x, w2i, i2w):
        self.batch_size = len(flist) 
        self.x = np.zeros((len_x, self.batch_size), dtype = np.int64)
        self.y = np.zeros((len_x, self.batch_size), dtype = np.int64)
        self.x_mask = np.zeros((len_x, self.batch_size))
        self.y_mask = np.zeros((len_x, self.batch_size))

        for idx_doc in xrange(len(flist)):
            content = flist[idx_doc]
            for idx_word in xrange(len(content)-1):
                w = content[idx_word]
                w1 = content[idx_word + 1]
                self.x[idx_word, idx_doc] = w
                self.y[idx_word, idx_doc] = w1
                self.x_mask[idx_word, idx_doc] = 1
                self.y_mask[idx_word, idx_doc] = 1

def get_data(xy_list, lex_x, w2i, i2w):
    return BatchData(xy_list, lex_x, w2i, i2w)

# limit memory
def batch_index(seqs, i2w, w2i, batch_size):
    data_xy = {}
    batch_x = []
    batch_y = []
    seqs_len = []
    batch_id = 0
    for i in xrange(len(seqs)):
        batch_x.append(i)
        batch_y.append(i)
        if len(batch_x) == batch_size or (i == len(seqs) - 1):
            data_xy[batch_id] = [batch_x, batch_y, [], len(batch_x)]
            batch_x = []
            batch_y = []
            batch_id += 1
    return data_xy

def index2seqs(lines, x_index, w2i):
    seqs = []
    for i in x_index:
        line = lines[i]
        x = np.zeros((len(line), len(w2i)))
        for j in range(0, len(line)):
            x[j, w2i[line[j]]] = 1
        seqs.append(np.asmatrix(x))

    data_xy = {}
    batch_x = []
    batch_y = []
    seqs_len = []
    batch_id = 0
    dim = len(w2i)
    zeros_m = np.zeros((1, dim))
    for i in xrange(len(seqs)):
        seq = seqs[i];
        X = seq[0 : len(seq) - 1, ]
        Y = seq[1 : len(seq), ]
        batch_x.append(X)
        seqs_len.append(X.shape[0])
        batch_y.append(Y)

    max_len = np.max(seqs_len);
    mask = np.zeros((max_len, len(batch_x)))
    concat_X = np.zeros((max_len, len(batch_x), dim))
    concat_Y = concat_X.copy()
    
    for b_i in xrange(len(batch_x)):
        X = batch_x[b_i]
        Y = batch_y[b_i]
        mask[0 : X.shape[0], b_i] = 1
        for r in xrange(max_len - X.shape[0]):
            X = np.concatenate((X, zeros_m), axis=0)
            Y = np.concatenate((Y, zeros_m), axis=0)
        concat_X[:, b_i, :] = X 
        concat_Y[:, b_i, :] = Y
    return concat_X, concat_Y, mask, len(batch_x)

