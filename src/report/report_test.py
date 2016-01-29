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

"""Unit tests for report."""

from __future__ import print_function, division, unicode_literals

import json
import os
import re
import sys
import unittest

import bs4

sys.path.insert(1, os.path.join(os.path.dirname(__file__), '..'))
import report
import chrome_app.apis

MINIMAL_APP_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'tests', 'test_app_minimal')

MANIFEST_POWER = {
  'name': 'power',
  'status': 'partial',
  'coverage': 0.00,
  'dependencies': [],
  'warnings': [
    {
      'member': 'requestKeepAwake',
      'status': 'none',
      'text': 'Does nothing.'
    },
    {
      'member': 'releaseKeepAwake',
      'status': 'none',
      'text': 'Does nothing.'
    }
  ]
}

MANIFEST_RUNTIME = {
  'name': 'app.runtime',
  'status': 'none',
  'warnings': []
}

class TestGenerateSummary(unittest.TestCase):
  """Tests generate_summary."""

  def test_generate_summary(self):
    """Tests that generate_summary gives expected HTML."""
    ca_manifest = {
      'name': 'test app',
      'version': '1.0.0',
      'manifest_version': 2,
      'app': {'background': []}
    }
    apis = {
      'power': MANIFEST_POWER,
      'app.runtime': MANIFEST_RUNTIME
    }
    status = report.Status.PARTIAL
    warnings = ['this is a warning', 'this is also a warning with <b>html</b>']
    summary = report.generate_summary(ca_manifest, apis, status, warnings)
    summary = re.sub(r'\w+', ' ', summary)  # Ignore insignificant whitespace.
    self.assertEqual(bs4.BeautifulSoup(summary), bs4.BeautifulSoup(
      re.sub(r'\w+', ' ', """\
<section id="summary">
  <h2>Summary</h2>
  <span class="name">test app</span> was
  <span class="conversion-status partial">partially converted, with warnings.
  </span>
  <ul>
      <li>
        <span class="ca-feature none">chrome.app.runtime</span> was not
        polyfilled.
      </li>
      <li>
        <span class="ca-feature partial">chrome.power</span> was polyfilled.
      </li>
  </ul>
</section>
""")))

# TODO(alger): Test generate_general_warnings, generate_polyfilled, and
# generate_not_polyfilled.


class TestProcessUsage(unittest.TestCase):
  """Tests process_usage."""

  def test_no_apis(self):
    """Tests that if there are no APIs, then nothing changes."""
    apis = {}
    report.process_usage(apis, MINIMAL_APP_DIR)
    self.assertEqual(apis, {})

  def test_usages_added(self):
    """Tests that usages are added to the API info."""
    apis = {
      'power': MANIFEST_POWER,
      'app.runtime': MANIFEST_RUNTIME
    }
    usage = chrome_app.apis.usage(apis, MINIMAL_APP_DIR)
    report.process_usage(apis, usage)
    self.assertEqual(apis['power']['usage'],
      [('m\xfd other script.js',
        1,
        '// keep awakes\n'
            '<span class="ca-feature none">'
            'chrome.power.requestKeepAwake</span>();\n'
            '// the user is now awake\nnotAChromeAppCall();',
        0)])
    self.assertEqual(apis['app.runtime']['usage'],
      [('my scr\xedpt.js',
        0,
        '<span class="ca-feature none">'
          'chrome.app.runtime.onLaunched.addListener</span>(function() {\n'
          '  chrome.app.window.create(\'my \xedndex.html\');\n});\n',
        0)])


class TestHighlightRelevantLine(unittest.TestCase):
  """Tests highlight_relevant_line."""

  def setUp(self):
    self.apis = {
      'power': MANIFEST_POWER,
      'app.runtime': MANIFEST_RUNTIME
    }

  def test_empty_context(self):
    """Tests that highlighting an empty context returns the empty string."""
    highlighted = report.highlight_relevant_line("", 0, self.apis)
    self.assertEqual(highlighted, '')

  def test_context_with_no_api_usages(self):
    """Tests a context with no API usages is not highlighted."""
    context = """// hello world
javascript();
var fun = function() {
  anotherCall();
}"""
    highlighted = report.highlight_relevant_line(context, 2, self.apis)
    self.assertEqual(highlighted, context)

  def test_context_with_api_usages(self):
    """Tests a context with some API usages is highlighted."""
    context = """chrome.power.requestKeepAwake();
chrome.app.runtime.onLaunched.addListener(makeWindow);
notAChromeAppCall();"""

    highlighted = report.highlight_relevant_line(context, 0, self.apis)
    self.assertEqual(highlighted,
      """<span class="ca-feature none">chrome.power.requestKeepAwake</span>();
chrome.app.runtime.onLaunched.addListener(makeWindow);
notAChromeAppCall();""")

    highlighted = report.highlight_relevant_line(context, 1, self.apis)
    self.assertEqual(highlighted,
      """chrome.power.requestKeepAwake();
<span class="ca-feature none">chrome.app.runtime.onLaunched.addListener</span>\
(makeWindow);\nnotAChromeAppCall();""")


class TestMakeWarning(unittest.TestCase):
  """Tests make_warning."""

  def setUp(self):
    self.name = 'power'
    self.member = 'requestKeepAwake'
    self.text = 'Does nothing.'
    self.apis = {
      'power': MANIFEST_POWER,
      'app.runtime': MANIFEST_RUNTIME
    }

  def test_make_warning(self):
    """Tests warning correct and highlighted."""
    warning = report.make_warning(self.name, self.member, self.text, self.apis)
    self.assertEqual(warning,
        {'member': 'requestKeepAwake',
         'text': '<span class="ca-feature none">chrome.power.requestKeepAwake'
                 '</span>: Does nothing.'})


class TestManifestWarnings(unittest.TestCase):
  """Tests manifest_warnings."""

  def test_not_implemented_manifest_warnings(self):
    """Tests that not implemented warnings in the manifest are returned."""
    manifest = {
      'name': 'test',
      'status': 'partial',
      'warnings': ['member']
    }
    warnings = report.manifest_warnings(manifest, {'test': manifest})
    self.assertEqual(warnings,
        [{'member': 'member',
          'text': '<span class="ca-feature none">chrome.test.member</span>: '
                  'Not implemented in the polyfill.'}])

  def test_text_manifest_warnings(self):
    """Tests that text warnings in the manifest are returned."""
    manifest = {
      'name': 'test',
      'status': 'partial',
      'warnings': [
        {'member': 'member',
         'text': 'a warning',
         'status': 'partial'}]
    }
    warnings = report.manifest_warnings(manifest, {'test': manifest})
    self.assertEqual(warnings,
        [{'member': 'member',
          'text': '<span class="ca-feature partial">chrome.test.member</span>: '
                  'a warning'}])

  def test_list_manifest_warnings(self):
    """Tests that text warnings listed in the manifest are returned."""
    manifest = {
      'name': 'test',
      'status': 'partial',
      'warnings': [
        {'member': 'member',
         'text': ['warning A', 'warning B'],
         'status': 'partial'}]
    }
    warnings = report.manifest_warnings(manifest, {'test': manifest})
    self.assertEqual(warnings,
        [{'member': 'member',
          'text': '<span class="ca-feature partial">chrome.test.member</span>: '
                  'warning A'},
         {'member': 'member',
          'text': '<span class="ca-feature partial">chrome.test.member</span>: '
                  'warning B'},])

# TODO(alger): Test format_html.

if __name__ == '__main__':
  unittest.main()
