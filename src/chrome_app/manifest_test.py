#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright 2015 Google Inc. All Rights Reserved.
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

"""Unit-test chrome_app.manifest.
"""

import os
import sys
import unittest

import mock

import chrome_app.manifest as chrome_app_manifest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class TestVerify(unittest.TestCase):
  """Tests chrome_app.manifest.verify."""

  @mock.patch('chrome_app.manifest.logging')
  def test_empty(self, mock_logging):
    """Tests that an empty manifest errors."""
    with self.assertRaises(ValueError) as context:
      chrome_app_manifest.verify({})
    self.assertEqual(context.exception.message,
      'Chrome Apps must include a background script.')

  @mock.patch('chrome_app.manifest.logging')
  def test_almost_empty(self, mock_logging):
    """Tests that a manifest with only one required member errors or triggers
    warnings (depending on the member remaining).
    """
    chrome_app_manifest.verify({'app': {'background': ''}})
    mock_logging.warning.assert_has_calls([
      mock.call('Chrome Apps must include a version.'),
      mock.call('Chrome Apps must include a name.'),
      mock.call('Chrome Apps must have manifest version 2.'),
    ], any_order=True)
    with self.assertRaises(ValueError):
      chrome_app_manifest.verify({'manifest_version': 2})
    with self.assertRaises(ValueError):
      chrome_app_manifest.verify({'app': {}})
    with self.assertRaises(ValueError):
      chrome_app_manifest.verify({'version': '0.0.1'})

  @mock.patch('chrome_app.manifest.logging')
  def test_all_but_one(self, mock_logging):
    """Tests that a manifest with all but one required member errors or triggers
    a warning (depending on the member missing)."""
    chrome_app_manifest.verify({
      'app': {'background': ''},
      'name': '',
      'version': '0.0.1',
    })
    mock_logging.warning.assert_called_with(
      'Chrome Apps must have manifest version 2.')
    mock_logging.warning.reset_mock()

    chrome_app_manifest.verify({
      'manifest_version': 2,
      'app': {'background': ''},
      'version': '0.0.1',
    })
    mock_logging.warning.assert_called_with(
      'Chrome Apps must include a name.')
    mock_logging.warning.reset_mock()

    chrome_app_manifest.verify({
      'manifest_version': 2,
      'app': {'background': ''},
      'name': '',
    })
    mock_logging.warning.assert_called_with(
      'Chrome Apps must include a version.')

    with self.assertRaises(ValueError) as context:
      chrome_app_manifest.verify({
        'manifest_version': 2,
        'name': '',
        'version': '0.0.1',
      })
    self.assertEqual(context.exception.message,
      'Chrome Apps must include a background script.')

  def test_minimum_requirements(self):
    """Tests that a manifest fulfilling the minimum requirements returns None.
    """
    self.assertIsNone(chrome_app_manifest.verify({
      'manifest_version': 2,
      'app': {'background': ''},
      'name': '',
      'version': '0.0.1',
    }))

  @mock.patch('chrome_app.manifest.logging')
  def test_wrong_manifest_version(self, mock_logging):
    """Tests that a manifest with the wrong version number triggers a warning.
    """
    chrome_app_manifest.verify({
      'manifest_version': 1,
      'app': {'background': ''},
      'name': '',
      'version': '0.0.1',
    })
    mock_logging.warning.assert_called_with(
      'Chrome Apps must have manifest version 2, found manifest version %s.', 1)

  def test_no_background_script(self):
    """Tests that a manifest with no background script errors."""
    with self.assertRaises(ValueError):
      chrome_app_manifest.verify({
        'manifest_version': 2,
        'app': {},
        'name': '',
        'version': '0.0.1',
      })

  @mock.patch('chrome_app.manifest.logging')
  def test_warnings_for_unconverted_members(self, mock_logging):
    """Tests that a manifest with unconvertible members triggers a warning."""
    chrome_app_manifest.verify({
      'manifest_version': 2,
      'app': {'background': ''},
      'name': '',
      'version': '0.0.1',
      'unconvertible': True
    })
    mock_logging.warning.assert_called_with(
      'Manifest member `%s` will not be converted.', 'unconvertible')

  @mock.patch('chrome_app.manifest.logging')
  def test_no_warnings_for_convertible_members(self, mock_logging):
    """Tests that no warnings are triggered for convertible members."""
    convertible_members = {'short_name', 'default_locale', 'icons', 'author',
      'description'}
    for member in convertible_members:
      chrome_app_manifest.verify({
        'manifest_version': 2,
        'app': {'background': ''},
        'name': '',
        'version': '0.0.1',
        member: ''
      })
      self.assertFalse(mock_logging.warning.called)

class TestGet(unittest.TestCase):
  """Tests chrome_app.manifest.get.

  This is tested on a "real world" application test_app, which is expected to
  exist in the root test folder (i.e., ../test_app_minimal).
  """
  def test_get(self):
    """Tests that get returns the correct app manifest."""
    minimal_path = os.path.join(
        os.path.dirname(ROOT_DIR), 'tests', 'test_app_minimal')
    manifest = chrome_app_manifest.get(minimal_path)
    self.assertEqual(manifest,
      {
      'app': {
        'background': {
          'scripts': ['a_background_script.js']
        }
      },
      'manifest_version': 2,
      'name': 'Minimal App',
      'version': '1.0.0'
    })

if __name__ == '__main__':
  unittest.main(verbosity=2)
