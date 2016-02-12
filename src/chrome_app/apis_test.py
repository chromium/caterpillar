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

"""Unit-test chrome_app.apis."""

from __future__ import print_function, division, unicode_literals

import collections
import os
import sys
import unittest

import mock

import caterpillar_test
import chrome_app.apis

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class TestApiMemberUsed(unittest.TestCase):
  """Tests api_member_used."""

  def test_no_member(self):
    """Tests that if there is no member, None is returned."""
    line = 'hello world, this is some téśt data!'
    member = chrome_app.apis.api_member_used(line)
    self.assertIsNone(member)

    line = 'hello world, this is some téśt data!'
    member = chrome_app.apis.api_member_used(line)
    self.assertIsNone(member)

  def test_api_member(self):
    """Tests that a member is picked up in the input string."""
    line = 'hello world, this test data uses chrome.tts.speak, test test.'
    member = chrome_app.apis.api_member_used(line)
    self.assertEqual(member, 'tts.speak')

    line = 'this test data uses chrome.app.runtime.onLaunched, test test.'
    member = chrome_app.apis.api_member_used(line)
    self.assertEqual(member, 'app.runtime.onLaunched')

  @unittest.skip('https://github.com/chromium/caterpillar/issues/28')
  def test_chrome_url(self):
    """Tests that chrome.google.com is not picked up as an API."""
    line = 'test test chrome.google.com test test'
    member = chrome_app.apis.api_member_used(line)
    self.assertIsNone(member)


class TestAppApis(caterpillar_test.TestCaseWithOutputDir):
  """Tests app_apis."""

  @unittest.skip('https://github.com/chromium/caterpillar/issues/28')
  def test_correct_output(self):
    apis = chrome_app.apis.app_apis(self.output_path)
    self.assertEqual(apis, [
      'app.runtime',
      'app.window',
      'power',
    ])


class TestUsage(caterpillar_test.TestCaseWithOutputDir):
  """Tests usage."""

  def test_no_apis(self):
    """Tests that if no APIs are provided, no usages are found."""
    usage = chrome_app.apis.usage([], self.output_path)
    self.assertEqual(usage, {})

  def test_correct_output(self):
    self.maxDiff = None
    usage = chrome_app.apis.usage(['app.runtime', 'app.window', 'power'],
                                  self.output_path)
    self.assertEqual(usage, {
      'app.runtime': collections.defaultdict(list, {'onLaunched.addListener': [(
            'my scrípt.js', 0,
            """chrome.app.runtime.onLaunched.addListener(function() {
  chrome.app.window.create('my índex.html');
});
""", 0)]}),
      'app.window': collections.defaultdict(list, {'create': [(
            'my scrípt.js', 1,
            """chrome.app.runtime.onLaunched.addListener(function() {
  chrome.app.window.create('my índex.html');
});
""", 0)]}),
      'power': collections.defaultdict(list, {'requestKeepAwake': [(
            'mý other script.js', 1,
            """// keep awakes
chrome.power.requestKeepAwake();
// the user is now awake
notAChromeAppCall();
""", 0)]}),
    })


if __name__ == '__main__':
  unittest.main()
