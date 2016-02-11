#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright 2016 Google Inc. All Rights Reserved.
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

"""End-to-end tests for Caterpillar."""

from __future__ import print_function, division, unicode_literals

import difflib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import caterpillar
import caterpillar_test

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
CATERPILLAR_PATH = os.path.join(TEST_DIR, 'caterpillar.py')
TTS_APP_NAME = 'test_app_tts'
TTS_REFERENCE_NAME = 'test_app_tts_output'
TTS_PATH = os.path.join(
    os.path.dirname(TEST_DIR), 'tests', TTS_APP_NAME)
TTS_REFERENCE_PATH = os.path.join(
    os.path.dirname(TEST_DIR), 'tests', TTS_REFERENCE_NAME)


class TestEndToEndConvert(caterpillar_test.TestCaseWithTempDir):
  """Converts an entire Chrome App and checks the output is correct."""

  @classmethod
  def setUpClass(cls):
    """Converts a test Chrome App."""
    cls.temp_path = tempfile.mkdtemp()
    cls.input_dir = TTS_PATH
    cls.output_dir = os.path.join(cls.temp_path, 'tts test output')
    cls.config_path = os.path.join(cls.temp_path, 'config.json')

    encoding = sys.getfilesystemencoding()

    cls.boilerplate_dir = 'caterpillar-📂'
    cls.report_dir = 'report ✓✓✓'
    cls.start_url = 'ttstest.html'
    config_input = '{}\n{}\n{}\n'.format(
        cls.boilerplate_dir, cls.report_dir, cls.start_url).encode(encoding)

    # Generate a config file using Caterpillar.
    process = subprocess.Popen(
        [CATERPILLAR_PATH, 'config', '-i', cls.config_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    process.communicate(input=config_input)
    if process.wait():
      raise subprocess.CalledProcessError()

    if not os.path.exists(cls.config_path):
      raise RuntimeError('Configuration file generation failed.')

    output = subprocess.check_output(
        [CATERPILLAR_PATH, 'convert', '-c', cls.config_path, cls.input_dir,
         cls.output_dir])

  @classmethod
  def tearDownClass(cls):
    """Deletes the converted Chrome App."""
    shutil.rmtree(cls.temp_path)

  def get_relative_filepaths(self, directory, ignore_directories=None):
    """Returns all relative filepaths in a directory and children.

    Args:
      directory: Path to directory.
      ignore_directories: Set of directory names to ignore. Any directory with
        one of these names, at any level of the hierarchy, will be ignored.

    Returns:
      set of relative filepaths.
    """
    if not ignore_directories:
      ignore_directories = set()
    filepaths = set()
    for dirname, dirnames, filenames in os.walk(directory, topdown=True):
      # Don't descend into ignored directories.
      for i in range(len(dirnames) - 1, -1, -1):
        if dirnames[i] in ignore_directories:
          del dirnames[i]

      for filename in filenames:
        relpath = os.path.relpath(os.path.join(dirname, filename), directory)
        filepaths.add(relpath)
    return filepaths

  def test_output_matches_reference(self):
    """Tests that the output matches the reference output."""
    expected_files = self.get_relative_filepaths(TTS_REFERENCE_PATH,
                                                 {'bower_components'})
    actual_files = self.get_relative_filepaths(self.output_dir,
                                               {'bower_components'})
    self.assertEqual(expected_files, actual_files)

  def test_all_correct_contents(self):
    """Tests that the content of all non-static output files is expected."""
    for dirname, _, filenames in os.walk(TTS_REFERENCE_PATH):
      for filename in filenames:
        if filename == caterpillar.SW_SCRIPT_NAME:
          # Service worker is partly random, so test it elsewhere.
          continue

        reference_path = os.path.join(dirname, filename)
        relpath = os.path.relpath(reference_path, TTS_REFERENCE_PATH)

        if not (relpath.startswith(self.boilerplate_dir)
                or relpath.startswith(self.report_dir)):
          output_path = os.path.join(self.output_dir, relpath)
          with open(reference_path) as reference_file:
            with open(output_path) as output_file:
              output_data = output_file.read().decode('utf-8')
              reference_data = reference_file.read().decode('utf-8')
              self.assertEqual(output_data, reference_data,
                  'Difference found in file `{}`.\n{}'.format(relpath,
                      '\n'.join(difflib.unified_diff(
                          output_data.split('\n'),
                          reference_data.split('\n'),
                          fromfile=reference_path,
                          tofile=output_path,
                          n=0))))

  def test_generated_service_worker(self):
    """Tests that the generated service worker is as expected."""
    output_sw_path = os.path.join(self.output_dir, caterpillar.SW_SCRIPT_NAME)
    reference_sw_path = os.path.join(
        TTS_REFERENCE_PATH, caterpillar.SW_SCRIPT_NAME)

    with open(output_sw_path) as output_file:
      with open(reference_sw_path) as reference_file:
        output_data = output_file.read().decode('utf-8')
        reference_data = reference_file.read().decode('utf-8')

        # The cache version is randomly generated in the output service worker,
        # so reset it to be 0, the same cache version as the reference service
        # worker.
        output_data = re.sub(
            r'CACHE_VERSION = \d+', 'CACHE_VERSION = 0', output_data)

        self.assertEqual(output_data, reference_data,
            'Difference found in file `{}`.\n{}'.format(
                caterpillar.SW_SCRIPT_NAME,
                '\n'.join(difflib.unified_diff(
                    output_data.split('\n'),
                    reference_data.split('\n'),
                    fromfile=reference_sw_path,
                    tofile=output_sw_path,
                    n=0))))


if __name__ == '__main__':
  unittest.main()
