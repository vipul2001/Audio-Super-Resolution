# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 20:52:19 2020

@author: vipul
"""

import numpy as np
import io

# ----------------------------------------------------------------------------

class DataSet(object):

  def __init__(self,path,
               fake_data=False,
               one_hot=False,
               dtype=None):
    datapoints,labels=io.load_h5(path)
    if labels is None:
      labels = np.zeros((len(datapoints),))

    if fake_data:
      self._num_examples = 10000
      self.one_hot = one_hot
    else:
      assert datapoints.shape[0] == labels.shape[0], (
          'datapoints.shape: %s labels.shape: %s' % (datapoints.shape, labels.shape))
      self._num_examples = datapoints.shape[0]

    self._datapoints = datapoints
    self._labels = labels
    self._epochs_completed = 0
    self._index_in_epoch = 0

  @property
  def datapoints(self):
    return self._datapoints

  @property
  def labels(self):
    return self._labels

  @property
  def num_examples(self):
    return self._num_examples

  @property
  def epochs_completed(self):
    return self._epochs_completed

  def __getitem__(self, batch_size, fake_data=False, shuffle=True):
    """Return the next `batch_size` examples from this data set."""
    if fake_data:
      fake_image = [1] * 784
      if self.one_hot:
        fake_label = [1] + [0] * 9
      else:
        fake_label = 0
      return [fake_image for x in range(batch_size)], [
          fake_label for x in range(batch_size)
      ]
    start = self._index_in_epoch
    # Shuffle for the first epoch
    if self._epochs_completed == 0 and start == 0 and shuffle:
      perm0 = np.arange(self._num_examples)
      np.random.shuffle(perm0)
      self._datapoints = self.datapoints[perm0]
      self._labels = self.labels[perm0]
    # Go to the next epoch
    if start + batch_size > self._num_examples:
      # Finished epoch
      self._epochs_completed += 1
      # Get the rest examples in this epoch
      rest_num_examples = self._num_examples - start
      datapoints_rest_part = self._datapoints[start:self._num_examples]
      labels_rest_part = self._labels[start:self._num_examples]
      # Shuffle the data
      if shuffle:
        perm = np.arange(self._num_examples)
        np.random.shuffle(perm)
        self._datapoints = self.datapoints[perm]
        self._labels = self.labels[perm]
      # Start next epoch
      start = 0
      self._index_in_epoch = batch_size - rest_num_examples
      end = self._index_in_epoch
      datapoints_new_part = self._datapoints[start:end]
      labels_new_part = self._labels[start:end]
      return np.concatenate((datapoints_rest_part, datapoints_new_part), axis=0) , np.concatenate((labels_rest_part, labels_new_part), axis=0)
    else:
      self._index_in_epoch += batch_size
      end = self._index_in_epoch
      return self._datapoints[start:end], self._labels[start:end]