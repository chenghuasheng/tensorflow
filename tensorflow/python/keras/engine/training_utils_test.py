# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for training utility functions."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

from tensorflow.python.framework import ops
from tensorflow.python.framework import test_util
from tensorflow.python.keras.engine import training_utils
from tensorflow.python.platform import test


class TrainingUtilTest(test.TestCase):

  @test_util.run_in_graph_and_eager_modes
  def test_convert_to_iterator_single_numpy(self):
    batch_size = 2
    a = np.ones([10, 10])
    iterator, steps_per_epoch = training_utils.convert_to_iterator(
        x=a, batch_size=batch_size)
    self.assertEquals(steps_per_epoch, 5)

    expected_batch = a[:batch_size, :]
    actual_batch, = iterator.get_next()
    self.assertAllEqual(expected_batch, actual_batch)

  @test_util.run_in_graph_and_eager_modes
  def test_convert_to_iterator_single_tensor(self):
    batch_size = 2
    a = ops.convert_to_tensor(np.ones([10, 10]))
    iterator, steps_per_epoch = training_utils.convert_to_iterator(
        x=a, batch_size=batch_size)
    self.assertEquals(steps_per_epoch, 5)

    expected_batch = a[:batch_size, :]
    actual_batch, = iterator.get_next()
    self.assertAllEqual(expected_batch, actual_batch)

  @test_util.run_in_graph_and_eager_modes
  def test_convert_to_iterator_y(self):
    batch_size = 2
    a = np.ones([10, 100])
    b = np.ones([10, 10])
    iterator, steps_per_epoch = training_utils.convert_to_iterator(
        x=a, y=b, batch_size=batch_size)
    self.assertEquals(steps_per_epoch, 5)

    expected_x = a[:batch_size, :]
    expected_y = b[:batch_size, :]
    actual_x, actual_y = iterator.get_next()
    self.assertAllEqual(expected_x, actual_x)
    self.assertAllEqual(expected_y, actual_y)

  @test_util.run_in_graph_and_eager_modes
  def test_convert_to_iterator_sample_weights(self):
    batch_size = 2
    a = ops.convert_to_tensor(np.ones([10, 100]))
    b = ops.convert_to_tensor(np.ones([10, 10]))
    sw = ops.convert_to_tensor(np.ones([10]))
    iterator, steps_per_epoch = training_utils.convert_to_iterator(
        x=a, y=b, sample_weights=sw, batch_size=batch_size)
    self.assertEquals(steps_per_epoch, 5)

    expected_x = a[:batch_size, :]
    expected_y = b[:batch_size, :]
    expected_sw = sw[:batch_size]
    actual_x, actual_y, actual_sw = iterator.get_next()
    self.assertAllEqual(expected_x, actual_x)
    self.assertAllEqual(expected_y, actual_y)
    self.assertAllEqual(expected_sw, actual_sw)

  @test_util.run_in_graph_and_eager_modes
  def test_convert_to_iterator_nested(self):
    batch_size = 2
    x = {'1': np.ones([10, 100]), '2': [np.zeros([10, 10]), np.ones([10, 20])]}
    iterator, steps_per_epoch = training_utils.convert_to_iterator(
        x=x, batch_size=batch_size)
    self.assertEquals(steps_per_epoch, 5)

    expected_x1 = x['1'][:batch_size, :]
    expected_x2_0 = x['2'][0][:batch_size, :]
    expected_x2_1 = x['2'][1][:batch_size, :]

    actual_x, = iterator.get_next()
    actual_x1 = actual_x['1'][:batch_size, :]
    actual_x2_0 = actual_x['2'][0][:batch_size, :]
    actual_x2_1 = actual_x['2'][1][:batch_size, :]

    self.assertAllEqual(expected_x1, actual_x1)
    self.assertAllEqual(expected_x2_0, actual_x2_0)
    self.assertAllEqual(expected_x2_1, actual_x2_1)

  @test_util.run_in_graph_and_eager_modes
  def test_convert_to_iterator_epochs(self):
    batch_size = 2
    a = np.ones([10, 10])
    iterator, steps_per_epoch = training_utils.convert_to_iterator(
        x=a, batch_size=batch_size, epochs=2)
    self.assertEquals(steps_per_epoch, 5)

    expected_batch = a[:batch_size, :]
    # loop through one whole epoch
    for _ in range(6):
      actual_batch, = iterator.get_next()
    self.assertAllEqual(expected_batch, actual_batch)

  @test_util.run_in_graph_and_eager_modes
  def test_convert_to_iterator_insufficient_info(self):
    # with batch_size and steps_per_epoch not set
    with self.assertRaises(ValueError):
      a = np.ones([10, 10])
      _ = training_utils.convert_to_iterator(x=a)

  def test_nested_all(self):
    nested_data = {'a': True, 'b': [True, True, (False, True)]}
    all_true = training_utils._nested_all(nested_data, lambda x: x)
    self.assertEquals(all_true, False)

    nested_data = {'a': True, 'b': [True, True, (True, True)]}
    all_true = training_utils._nested_all(nested_data, lambda x: x)
    self.assertEquals(all_true, True)

  def test_nested_any(self):
    nested_data = [False, {'a': False, 'b': (False, True)}]
    any_true = training_utils._nested_any(nested_data, lambda x: x)
    self.assertEquals(any_true, True)

    nested_data = [False, {'a': False, 'b': (False, False)}]
    any_true = training_utils._nested_any(nested_data, lambda x: x)
    self.assertEquals(any_true, False)


if __name__ == '__main__':
  test.main()
