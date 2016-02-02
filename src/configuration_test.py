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

"""Unit tests for configuration file generation."""

from __future__ import print_function, division, unicode_literals

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import mock

import configuration

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_PATH = os.path.join(TEST_DIR, 'configuration.py')


class TestStrToBool(unittest.TestCase):
  """Tests str_to_bool."""

  def test_str_to_bool(self):
    self.assertEqual(configuration.str_to_bool('true'), True)
    self.assertEqual(configuration.str_to_bool('TrUe'), True)
    self.assertEqual(configuration.str_to_bool('falsE'), False)
    self.assertEqual(configuration.str_to_bool('false'), False)
    self.assertRaises(ValueError, configuration.str_to_bool, 'notabool')


class TestGenerate(unittest.TestCase):
  """Tests generate."""

  def test_default(self):
    """Tests generating a default configuration."""
    self.assertEqual(configuration.generate(), {
        'boilerplate_dir': 'caterpillar',
        'report_dir': 'caterpillar-report',
        'start_url': 'index.html',
    })

  @mock.patch('__builtin__.raw_input', side_effect=(
      'caterpillar-📂', 'report ✓✓✓', 't✓e✓s✓t✓.html'))
  def test_interactive(self, mock_raw_input):
    """Tests interactively generating a configuration."""
    config = configuration.generate(True)
    self.assertEqual(config, {
        'boilerplate_dir': 'caterpillar-📂',
        'report_dir': 'report ✓✓✓',
        'start_url': 't✓e✓s✓t✓.html',
    })


class TestLoad(unittest.TestCase):
  """Tests load."""

  def setUp(self):
    """Makes a temporary  directory and stores it in self.temp_path."""
    self.temp_path = tempfile.mkdtemp()
    self.config_path = os.path.join(self.temp_path, '✓✓✓config✓✓✓.json')

  def tearDown(self):
    """Cleans up the temporary directory."""
    shutil.rmtree(self.temp_path)

  def test_load_valid(self):
    """Tests loading a valid config file returns the correct result."""
    config = {
      'boilerplate_dir': '♨ 📂 directory',
      'report_dir': '✒ 📂 directory',
      'start_url': '🚧 my 📄 website 🚧.html',
    }
    with open(self.config_path, 'w') as config_file:
      json.dump(config, config_file)

    loaded_config = configuration.load(self.config_path)

    self.assertEqual(loaded_config, config)

  @mock.patch('configuration.logging')
  def test_warn_on_missing_options(self, mock_logging):
    """Tests that loading a config file missing options causes warnings."""
    config = {
      'boilerplate_dir': '♨ 📂 directory',
    }
    with open(self.config_path, 'w') as config_file:
      json.dump(config, config_file)

    configuration.load(self.config_path)

    mock_logging.warning.assert_called_with(
      'Configuration file `%s` missing options: %s', self.config_path,
      'report_dir, start_url')

  @mock.patch('configuration.logging')
  def test_warn_on_unknown_options(self, mock_logging):
    """Tests that loading a config file with unknown options causes warnings."""
    config = {
      'boilerplate_dir': '♨ 📂 directory',
      'report_dir': '✒ 📂 directory',
      'start_url': '🚧 my 📄 website 🚧.html',
      'year': '2007',
      '📄': ' 📄 📄 📄 📄',
    }
    with open(self.config_path, 'w') as config_file:
      json.dump(config, config_file)

    configuration.load(self.config_path)

    mock_logging.warning.assert_called_with(
      'Configuration file `%s` has unexpected options: %s', self.config_path,
      'year, 📄')

  def test_not_found_raises(self):
    """Tests that if the given path does not exist, then an error is raised."""
    self.assertRaises(IOError, configuration.load, 'non-existent path')

  def test_invalid_json_raises(self):
    """Tests that an error is raised for invalid JSON in a config file."""
    with open(self.config_path, 'w') as config_file:
      config_file.write("""{ not valid json }""")

    self.assertRaises(ValueError, configuration.load, self.config_path)


class TestMissingOptions(unittest.TestCase):
  """Tests missing_options."""

  def test_missing_options(self):
    """Tests that missing_options returns correct result."""
    config = {'hello': 'world', 'report_dir': 'this'}
    self.assertEqual(configuration.missing_options(config),
                     ['boilerplate_dir', 'start_url'])


class TestUnexpectedOptions(unittest.TestCase):
  """Tests unexpected_options."""

  def test_unexpected_options(self):
    """Tests that unexpected_options returns correct result."""
    config = {'hello': 'world', 'report_dir': 'this', 'world': 'hello'}
    self.assertEqual(configuration.unexpected_options(config),
                     ['hello', 'world'])


if __name__ == '__main__':
  unittest.main()
