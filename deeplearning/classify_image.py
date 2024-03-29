# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
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

"""Simple image classification with Inception.

Run image classification with Inception trained on ImageNet 2012 Challenge data
set.

This program creates a graph from a saved GraphDef protocol buffer,
and runs inference on an input JPEG image. It outputs human readable
strings of the top 5 predictions along with their probabilities.

Change the --image_file argument to any jpg image to compute a
classification of that image.

Please see the tutorial and website for a detailed description of how
to use this script to perform image recognition.

https://tensorflow.org/tutorials/image_recognition/
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import re
import sys
import tarfile

import numpy as np
from six.moves import urllib
import tensorflow as tf

import argparse
import glob
import cPickle as pickle

OUTPUT_PROBABILITIES = "output_probabilities.txt"




FLAGS = tf.app.flags.FLAGS

# classify_image_graph_def.pb:
#   Binary representation of the GraphDef protocol buffer.
# imagenet_synset_to_human_label_map.txt:
#   Map from synset ID to a human readable string.
# imagenet_2012_challenge_label_map_proto.pbtxt:
#   Text representation of a protocol buffer mapping a label to synset ID.
tf.app.flags.DEFINE_string(
    'model_dir', '/tmp/imagenet',
    """Path to classify_image_graph_def.pb, """
    """imagenet_synset_to_human_label_map.txt, and """
    """imagenet_2012_challenge_label_map_proto.pbtxt.""")

tf.app.flags.DEFINE_string('image_file', '',   ### here you can indicate the image file !!
                           """Absolute path to image file.""")
tf.app.flags.DEFINE_integer('num_top_predictions', 5,
                            """Display this many predictions.""")

# pylint: disable=line-too-long
DATA_URL = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'
# pylint: enable=line-too-long


def create_graph():
  """Creates a graph from saved GraphDef file and returns a saver."""
  # Creates graph from saved graph_def.pb.

  with tf.gfile.FastGFile(os.path.join(
      '/tmp/imagenet', 'classify_image_graph_def.pb'), 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    pythonGraph = tf.import_graph_def(graph_def, name='')

def create_session():
  maybe_download_and_extract()

  create_graph()
  sess = tf.Session()
  softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')
  return sess, softmax_tensor

def run_inference_on_query_image(sess, imagePath, softmax_tensor):
  # tf.app.run()
  # maybe_download_and_extract()


  # sess = create_session()
  # with tf.Session() as sess:

  # use glob to grab the image paths and loop over them
      # extract the image ID (i.e. the unique filename) from the image
      # path and load the image itself
  # Store dictionary
  # tf.app.flags.DEFINE_string('image_file', imagePath,   ### here you can indicate the image file"""Absolute path to image file.""")
  if not tf.gfile.Exists(imagePath):
    tf.logging.fatal('File does not exist %s', imagePath)
  image_data = tf.gfile.FastGFile(imagePath, 'rb').read()
  imageID = imagePath[imagePath.rfind("/") + 1:]

  predictions = sess.run(softmax_tensor,
                         {'DecodeJpeg/contents:0': image_data})
  predictions = np.squeeze(predictions)
  return predictions


def run_inference_on_image(image_dir):
  """Runs inference on an image.

  Args:
    image: Image file name.

  Returns:
    Nothing
  """

  # Creates graph from saved GraphDef.
  create_graph()

  with tf.Session() as sess:
    # Some useful tensors:
    # 'softmax:0': A tensor containing the normalized prediction across
    #   1000 labels.
    # 'pool_3:0': A tensor containing the next-to-last layer containing 2048
    #   float description of the image.
    # 'DecodeJpeg/contents:0': A tensor containing a string providing JPEG
    #   encoding of the image.
    # Runs the softmax tensor by feeding the image_data as input to the graph.
    softmax_tensor = sess.graph.get_tensor_by_name('softmax:0')



    dict_imgid_prob = {}
    # use glob to grab the image paths and loop over them
        # extract the image ID (i.e. the unique filename) from the image
        # path and load the image itself
    # Store dictionary
    for imagePath in image_dir:
      # tf.app.flags.DEFINE_string('image_file', imagePath,   ### here you can indicate the image file"""Absolute path to image file.""")
      if not tf.gfile.Exists(imagePath):
        tf.logging.fatal('File does not exist %s', imagePath)
      image_data = tf.gfile.FastGFile(imagePath, 'rb').read()
      imageID = imagePath[imagePath.rfind("/") + 1:]

      predictions = sess.run(softmax_tensor,
                             {'DecodeJpeg/contents:0': image_data})
      predictions = np.squeeze(predictions)
      dict_imgid_prob[imageID] = predictions
    # print("Vector length: ", len(predictions))

    # for dim in range(len(predictions)):
    #   print('%.5f ' % predictions[dim])

    file_dictionary = open(OUTPUT_PROBABILITIES, "wb")
    pickle.dump(dict_imgid_prob, file_dictionary)
    file_dictionary.close()


def maybe_download_and_extract():
  """Download and extract model tar file."""
  dest_directory = FLAGS.model_dir
  if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)
  filename = DATA_URL.split('/')[-1]
  filepath = os.path.join(dest_directory, filename)
  if not os.path.exists(filepath):
    def _progress(count, block_size, total_size):
      sys.stdout.write('\r>> Downloading %s %.1f%%' % (
          filename, float(count * block_size) / float(total_size) * 100.0))
      sys.stdout.flush()
    filepath, _ = urllib.request.urlretrieve(DATA_URL, filepath, _progress)
    print()
    statinfo = os.stat(filepath)
    print('Succesfully downloaded', filename, statinfo.st_size, 'bytes.')
  tarfile.open(filepath, 'r:gz').extractall(dest_directory)


def main(_):
  maybe_download_and_extract()

  # image = (FLAGS.image_file if FLAGS.image_file else
  #          os.path.join(FLAGS.model_dir, 'cropped_panda.jpg'))
  # feature_vec = run_inference_on_image([image])
  
  img_dir = glob.glob(args["dataset"] + "/*.jpg")
  run_inference_on_image(img_dir)


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required = False, default='../ImageData/train/data/*/',
    help = "Path to the directory that contains the images to be indexed")
ap.add_argument("-i", "--index", required = False, default='index.csv',
    help = "Path to where the computed index will be stored")
args = vars(ap.parse_args())



if __name__ == '__main__':
  tf.app.run()
