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

"""Unit tests for Caterpillar."""

from __future__ import print_function, division, unicode_literals

import codecs
import copy
import difflib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import bs4

import caterpillar

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
MINIMAL_APP_NAME = 'test_app_minimal'
MINIMAL_PATH = os.path.join(
    os.path.dirname(TEST_DIR), 'tests', MINIMAL_APP_NAME)
BOILERPLATE_DIR = 'bóilerplate dir'
REPORT_DIR = 'réport dir'

# Base classes for test cases with similar setups.


class TestCaseWithTempDir(unittest.TestCase):
  """Base test case for tests that require a temporary directory."""

  def setUp(self):
    """Makes a temporary  directory and stores it in self.temp_path."""
    self.temp_path = tempfile.mkdtemp()

  def tearDown(self):
    """Cleans up the temporary directory."""
    shutil.rmtree(self.temp_path)


class TestCaseWithOutputDir(TestCaseWithTempDir):
  """Base test case for tests that require an output web app directory."""

  def setUp(self):
    """Makes a temporary output directory and stores it in self.output_path.
    """
    super(TestCaseWithOutputDir, self).setUp()
    self.output_path = os.path.join(self.temp_path, MINIMAL_APP_NAME)
    caterpillar.setup_output_dir(MINIMAL_PATH, self.output_path,
                                 BOILERPLATE_DIR, REPORT_DIR)


# Test cases.


class TestSetupOutputDir(TestCaseWithTempDir):
  """Tests setup_output_dir."""

  def setUp(self):
    """Makes a path to an output web app and stores it in self.output_path."""
    super(TestSetupOutputDir, self).setUp()
    self.output_path = os.path.join(self.temp_path, MINIMAL_APP_NAME)

  def test_setup_output_dir_makes_dir(self):
    """Tests that setup_output_dir makes the expected output directory."""
    caterpillar.setup_output_dir(MINIMAL_PATH, self.output_path,
                                 BOILERPLATE_DIR, REPORT_DIR)
    self.assertTrue(os.path.isdir(self.output_path))

  def test_setup_output_dir_makes_boilerplate_dir(self):
    """Tests that setup_output_dir makes a boilerplate directory."""
    caterpillar.setup_output_dir(MINIMAL_PATH, self.output_path,
                                 BOILERPLATE_DIR, REPORT_DIR)
    self.assertTrue(
        os.path.isdir(os.path.join(self.output_path, BOILERPLATE_DIR)))

  def test_setup_output_dir_makes_report_dir(self):
    """Tests that setup_output_dir makes a report directory."""
    caterpillar.setup_output_dir(MINIMAL_PATH, self.output_path,
                                 BOILERPLATE_DIR, REPORT_DIR)
    self.assertTrue(
        os.path.isdir(os.path.join(self.output_path, REPORT_DIR)))

  def test_setup_output_dir_makes_polyfill_dir(self):
    """Tests that setup_output_dir makes a polyfill directory."""
    caterpillar.setup_output_dir(
        MINIMAL_PATH, self.output_path, BOILERPLATE_DIR, REPORT_DIR)
    self.assertTrue(os.path.isdir(
        os.path.join(self.output_path, BOILERPLATE_DIR, 'polyfills')))

  def test_setup_output_dir_copies_all_files(self):
    """Tests that setup_output_dir copies all input files to the output app."""
    caterpillar.setup_output_dir(
        MINIMAL_PATH, self.output_path, BOILERPLATE_DIR, REPORT_DIR)
    for root, _, files in os.walk(MINIMAL_PATH):
      for name in files:
        relpath = os.path.relpath(os.path.join(root, name), MINIMAL_PATH)
        path = os.path.join(self.output_path, relpath)
        self.assertTrue(os.path.exists(path))

  def test_setup_output_dir_no_unexpected_files(self):
    """Tests that setup_output_dir doesn't add any unexpected files."""
    caterpillar.setup_output_dir(
        MINIMAL_PATH, self.output_path, BOILERPLATE_DIR, REPORT_DIR)
    for root, _, files in os.walk(self.output_path):
      for name in files:
        relpath = os.path.relpath(os.path.join(root, name), self.output_path)
        path = os.path.join(MINIMAL_PATH, relpath)
        self.assertTrue(os.path.exists(path))

  def test_setup_output_dir_force_false(self):
    """Tests that force=False disallows overwriting of an existing directory."""
    os.mkdir(self.output_path)
    with self.assertRaises(OSError) as e:
      caterpillar.setup_output_dir(
          MINIMAL_PATH, self.output_path, BOILERPLATE_DIR, REPORT_DIR)
    self.assertEqual(e.exception.message, 'Output directory already exists.')

  def test_setup_output_dir_force_true_copies_all_files(self):
    """Tests that force=True allows overwriting of an existing directory."""
    os.mkdir(self.output_path)
    caterpillar.setup_output_dir(
        MINIMAL_PATH, self.output_path, BOILERPLATE_DIR, REPORT_DIR, force=True)
    for root, _, files in os.walk(MINIMAL_PATH):
      for name in files:
        relpath = os.path.relpath(os.path.join(root, name), MINIMAL_PATH)
        path = os.path.join(self.output_path, relpath)
        self.assertTrue(os.path.exists(path))

  def test_setup_output_dir_force_true_deletes_existing_files(self):
    """Tests that force=True deletes files in existing directory."""
    os.mkdir(self.output_path)
    test_filename = 'existing file'
    with open(os.path.join(self.output_path, test_filename), 'w') as f:
      pass

    caterpillar.setup_output_dir(
        MINIMAL_PATH, self.output_path, BOILERPLATE_DIR, REPORT_DIR, force=True)

    self.assertFalse(
        os.path.exists(os.path.join(self.output_path, test_filename)))


class TestCleanupOutputDir(TestCaseWithOutputDir):
  """Tests cleanup_output_dir."""

  def test_no_manifest(self):
    """Tests that the manifest is removed."""
    caterpillar.cleanup_output_dir(self.output_path)
    self.assertFalse(
        os.path.exists(os.path.join(self.output_path, 'manifest.json')))


class TestCopyStaticCode(TestCaseWithOutputDir):
  """Tests copy_static_code."""

  def test_no_copy(self):
    """Tests copying no files."""
    existing_files = []
    for root, _, files in os.walk(self.output_path):
      for name in files:
        existing_files.append(os.path.join(root, name))
    caterpillar.copy_static_code([], self.output_path, BOILERPLATE_DIR)
    for root, _, files in os.walk(self.output_path):
      for name in files:
        path = os.path.join(root, name)
        self.assertIn(path, existing_files, 'File {} was copied.'.format(path))

  def test_copy_one(self):
    """Tests copying one file."""
    for to_copy in ['register_sw.js', 'sw_static.js',
                    os.path.join('polyfills', 'tts.polyfill.js')]:
      caterpillar.copy_static_code([to_copy], self.output_path, BOILERPLATE_DIR)
      self.assertTrue(
          os.path.exists(
              os.path.join(self.output_path, BOILERPLATE_DIR, to_copy)),
          'File {} was not copied.'.format(to_copy))

  def test_copy_many(self):
    """Tests copying many files."""
    to_copy = ['register_sw.js', 'sw_static.js',
               os.path.join('polyfills', 'tts.polyfill.js')]
    caterpillar.copy_static_code(to_copy, self.output_path, BOILERPLATE_DIR)
    for filename in to_copy:
      self.assertTrue(
          os.path.exists(
              os.path.join(self.output_path, BOILERPLATE_DIR, filename)),
          'File {} was not copied.'.format(filename))


class TestGenerateWebManifest(unittest.TestCase):
  """Tests generate_web_manifest."""

  def test_minimal_manifest(self):
    """Tests correct web manifest for a minimal Chrome App manifest."""
    chrome_app_manifest = {
      'app': {
        'background': {
          'scripts': ['a_background_script.js']
        }
      },
      'manifest_version': 2,
      'name': 'Minimal App',
      'version': '1.0.0'
    }
    web_manifest = caterpillar.generate_web_manifest(chrome_app_manifest, '.')
    self.assertEqual(web_manifest['name'], 'Minimal App')
    self.assertEqual(web_manifest['short_name'], 'Minimal App')
    self.assertEqual(web_manifest['lang'], 'en')
    self.assertEqual(web_manifest['splash_screens'], [])
    self.assertEqual(web_manifest['display'], 'minimal-ui')
    self.assertEqual(web_manifest['orientation'], 'any')
    self.assertEqual(web_manifest['start_url'], '.')
    self.assertEqual(web_manifest['theme_color'], 'white')
    self.assertEqual(web_manifest['background_color'], 'white')
    self.assertEqual(web_manifest['related_applications'], [])
    self.assertEqual(web_manifest['prefer_related_applications'], False)
    self.assertEqual(web_manifest['icons'], [])

  def test_complete_manifest(self):
    """Tests correct web manifest for a complete Chrome App manifest."""
    # Sample manifest taken from https://developer.chrome.com/apps/manifest,
    # with some elements removed and/or edited.
    chrome_app_manifest = {
      'app': {
        'background': {
          'scripts': ['a_background_script.js']
        }
      },
      'manifest_version': 2,
      'name': 'Minimal App',
      'version': '1.0.0',
      'default_locale': 'fr',
      'description': 'A plain text description',
      'icons': {
          '16': 'icon16.png',
          '128': 'icon128.png'
      },
      'author': 'anon',
      'bluetooth': {
        'uuids': ['110101', '2323']
      },
      'current_locale': 'de',
      'key': 'test34',
      'minimum_chrome_version': '1.0.0',
      'optional_permissions': ['tabs'],
      'permissions': ['tabs'],
      'platforms': ['windows'],
      'short_name': 'testapp3223',
      'version_name': '12.20.102',
      'webview': {
        "partitions": [
          {
            "name": "static",
            "accessible_resources": ["header.html", "footer.html", "static.png"]
          },
        ]
      }
    }

    web_manifest = caterpillar.generate_web_manifest(chrome_app_manifest, '.')
    self.assertEqual(web_manifest['name'], chrome_app_manifest['name'])
    self.assertEqual(
        web_manifest['short_name'], chrome_app_manifest['short_name'])
    self.assertEqual(
        web_manifest['lang'], chrome_app_manifest['default_locale'])
    self.assertEqual(web_manifest['splash_screens'], [])
    self.assertEqual(web_manifest['display'], 'minimal-ui')
    self.assertEqual(web_manifest['orientation'], 'any')
    self.assertEqual(web_manifest['start_url'], '.')
    self.assertEqual(web_manifest['theme_color'], 'white')
    self.assertEqual(web_manifest['background_color'], 'white')
    self.assertEqual(web_manifest['related_applications'], [])
    self.assertEqual(web_manifest['prefer_related_applications'], False)
    self.assertItemsEqual(web_manifest['icons'], [{
      'src': 'icon128.png',
      'sizes': '128x128'
    }, {
      'src': 'icon16.png',
      'sizes': '16x16'
    }])


class TestInjectScriptTags(unittest.TestCase):
  """Tests inject_script_tags."""

  def setUp(self):
    """Stores a BeautifulSoup in self.soup."""
    html = """
<!DOCTYPE html>
<html>
 <head>
  <meta charset="utf-8"/>
  <title>
   Héllø World
  </title>
  <link href="styles/main.css" rel="stylesheet"/>
  <meta content="Hello World" name="name"/>
 </head>
 <body>
  <h1>
   Hello, Wo®ld!
  </h1>
 </body>
</html>"""
    self.soup = bs4.BeautifulSoup(html)

  def test_no_requirements(self):
    """Tests no tags are injected if there are no requirements."""
    init_soup = copy.copy(self.soup)
    caterpillar.inject_script_tags(self.soup, [], '.', BOILERPLATE_DIR, '')
    self.assertEqual(self.soup, init_soup)

  def test_one_requirement(self):
    """Tests the correct tag is injected if there is one requirement."""
    requirement = 'mísc.javascript'
    caterpillar.inject_script_tags(
        self.soup, [requirement], 'path', BOILERPLATE_DIR, '')
    self.assertIsNotNone(
        self.soup.find('script',
                       src=os.path.join('path', BOILERPLATE_DIR, requirement)))

  def test_many_requirements_tag_existence(self):
    """Tests the correct tags are injected if there are many requirements."""
    requirements = ['réq', 'uir', 'edf', 'ile', 's.j', 'ava', 'scr', 'ipt']
    caterpillar.inject_script_tags(
      self.soup, requirements, 'path', BOILERPLATE_DIR, '')
    for requirement in requirements:
      self.assertIsNotNone(
          self.soup.find('script',
                         src=os.path.join('path', BOILERPLATE_DIR,
                                          requirement)))

  def test_many_requirements_tag_order(self):
    """Tests tags are injected in order."""
    requirements = ['réq', 'uir', 'edf', 'ile', 's.j', 'ava', 'scr', 'ipt']
    caterpillar.inject_script_tags(
        self.soup, requirements, 'path', BOILERPLATE_DIR, '')
    srcs = [script['src'] for script in self.soup('script')]
    upto = -1
    for requirement in requirements:
      # Monotonically increasing indices <-> order is preserved.
      index = srcs.index(os.path.join('path', BOILERPLATE_DIR, requirement))
      self.assertGreater(index, upto)
      upto = index


class TestInjectMiscTags(unittest.TestCase):
  """Tests inject_misc_tags."""

  def setUp(self):
    """Stores a BeautifulSoup in self.soup."""
    html = """
<!DOCTYPE html>
<html>
 <head>
  <title>
   Hello Wó®ld
  </title>
  <link href="styles/main.css" rel="stylesheet"/>
 </head>
 <body>
  <h1>
   Héllo, World! ÚÑÍ¢ÓÐÉ
  </h1>
 </body>
</html>"""
    self.soup = bs4.BeautifulSoup(html)

  def test_manifest_link(self):
    """Tests that the manifest link tag is added and correct."""
    chrome_app_manifest = {}
    root_path = 'path'
    caterpillar.inject_misc_tags(self.soup, chrome_app_manifest, root_path, '')
    link = self.soup.find('link', rel='manifest')
    self.assertIsNotNone(link)
    self.assertEqual(link['href'],
                     os.path.join(root_path, 'manifest.webmanifest'))

  def test_meta_charset(self):
    """Tests that the meta charset tag is added and correct."""
    chrome_app_manifest = {}
    root_path = 'path'
    caterpillar.inject_misc_tags(self.soup, chrome_app_manifest, root_path, '')
    meta = self.soup.find('meta', charset='utf-8')
    self.assertIsNotNone(meta)

  def test_no_duplicate_metas(self):
    """Tests that existing meta tags aren't duplicated."""
    chrome_app_manifest = {'description': 'a déscription'}
    root_path = 'path'
    html = """
<!DOCTYPE html>
<html>
 <head>
  <title>
   Hello Wó®ld
  </title>
  <meta name="description" content="tést description"/>
  <link href="styles/main.css" rel="stylesheet"/>
 </head>
 <body>
  <h1>
   Héllo, World! ÚÑÍ¢ÓÐÉ
  </h1>
 </body>
</html>"""
    soup = bs4.BeautifulSoup(html)
    caterpillar.inject_misc_tags(soup, chrome_app_manifest, root_path, '')
    metas = soup.findAll('meta', {'name': 'description'})
    self.assertEqual(len(metas), 1)
    self.assertEqual(metas[0]['content'], 'tést description')

  def test_meta_description(self):
    """Tests that the meta description tag is added and correct."""
    chrome_app_manifest = {'description': 'a déscription'}
    root_path = 'path'
    caterpillar.inject_misc_tags(self.soup, chrome_app_manifest, root_path, '')
    meta = self.soup.find('meta', {'name': 'description'})
    self.assertIsNotNone(meta)
    self.assertEqual(meta['content'], chrome_app_manifest['description'])

  def test_meta_author(self):
    """Tests that the meta author tag is added and correct."""
    chrome_app_manifest = {'author': 'an áuthor'}
    root_path = 'path'
    caterpillar.inject_misc_tags(self.soup, chrome_app_manifest, root_path, '')
    meta = self.soup.find('meta', {'name': 'author'})
    self.assertIsNotNone(meta)
    self.assertEqual(meta['content'], chrome_app_manifest['author'])

  def test_meta_name(self):
    """Tests that the meta name tag is added and correct."""
    chrome_app_manifest = {'name': 'a náme'}
    root_path = 'path'
    caterpillar.inject_misc_tags(self.soup, chrome_app_manifest, root_path, '')
    meta = self.soup.find('meta', {'name': 'name'})
    self.assertIsNotNone(meta)
    self.assertEqual(meta['content'], chrome_app_manifest['name'])

  def test_no_head(self):
    """Tests that the manifest link tag is added even with no head."""
    chrome_app_manifest = {}
    root_path = 'path'
    html = """\
<!DOCTYPE html>
<html>
 <body>
  <h1>
   Héllo, World! ÚÑÍ¢ÓÐÉ
  </h1>
 </body>
</html>"""
    soup = bs4.BeautifulSoup(html, 'html.parser')
    caterpillar.inject_misc_tags(soup, chrome_app_manifest, root_path, '')
    self.assertEqual(unicode(soup), """\
<!DOCTYPE html>

<html><head><meta charset="utf-8"/><link href="path/manifest.webmanifest"\
 rel="manifest"/></head>
<body>
<h1>
   Héllo, World! ÚÑÍ¢ÓÐÉ
  </h1>
</body>
</html>""")


  def test_no_head_or_html(self):
    """Tests that the manifest link tag is added with no head or html tags."""
    chrome_app_manifest = {}
    root_path = 'path'
    html = """
<!DOCTYPE html>
<body>
<h1>
 Héllo, World! ÚÑÍ¢ÓÐÉ
</h1>
</body>"""
    soup = bs4.BeautifulSoup(html, 'html.parser')
    caterpillar.inject_misc_tags(soup, chrome_app_manifest, root_path, '')
    self.assertEqual(unicode(soup), """\
<head><meta charset="utf-8"/><link href="path/manifest.webmanifest"\
 rel="manifest"/></head>
<!DOCTYPE html>

<body>
<h1>
 Héllo, World! ÚÑÍ¢ÓÐÉ
</h1>
</body>""")


class TestInsertTodosIntoFile(TestCaseWithTempDir):
  """Tests insert_todos_into_file."""

  def test_no_todos(self):
    """Tests that if there are no TODOs to add, nothing is changed."""
    js = """// héllo world
unrelated.app.call();"""
    filename = 'test.js'
    filepath = os.path.join(self.temp_path, filename)
    with codecs.open(filepath, 'w', encoding='utf-8') as js_file:
      js_file.write(js)

    caterpillar.insert_todos_into_file(filepath)

    with codecs.open(filepath, encoding='utf-8') as js_file:
      self.assertEqual(js, js_file.read())

  def test_top_level_todos(self):
    """Tests TODOs are inserted for top-level API calls like chrome.tts.speak.
    """
    js = """// héllo world
chrome.tts.speak('héllø');
chrome.unrelated.call();
unrelated.app.call();"""
    filename = 'test.js'
    filepath = os.path.join(self.temp_path, filename)
    with codecs.open(filepath, 'w', encoding='utf-8') as js_file:
      js_file.write(js)

    caterpillar.insert_todos_into_file(filepath)

    with codecs.open(filepath, encoding='utf-8') as js_file:
      js = js_file.read()
      self.assertEqual(js, """// héllo world
// TODO(Caterpillar): Check usage of tts.speak.
chrome.tts.speak('héllø');
// TODO(Caterpillar): Check usage of unrelated.call.
chrome.unrelated.call();
unrelated.app.call();""")

  def test_deeper_todos(self):
    """Tests TODOs are inserted for deeper API calls.

    Deep API calls include members like chrome.storage.onChanged.addListener,
    and have more than two levels of membership."""
    js = """// hello world
chrome.storage.onChanged.addListener(function() {});
unrelated.app.call();"""
    filename = 'test.js'
    filepath = os.path.join(self.temp_path, filename)
    with codecs.open(filepath, 'w', encoding='utf-8') as js_file:
      js_file.write(js)

    caterpillar.insert_todos_into_file(filepath)

    with codecs.open(filepath, encoding='utf-8') as js_file:
      js = js_file.read()
      self.assertEqual(js, """// hello world
// TODO(Caterpillar): Check usage of storage.onChanged.addListener.
chrome.storage.onChanged.addListener(function() {});
unrelated.app.call();""")


class TestGenerateServiceWorker(TestCaseWithOutputDir):
  """Tests generate_service_worker."""

  def test_all_files_cached(self):
    """Tests that the generated service worker caches all files."""
    chrome_app_manifest = {
      'app': {'background': {}}
    }
    service_worker = caterpillar.generate_service_worker(
        self.output_path, chrome_app_manifest, [], BOILERPLATE_DIR)
    cache_list = re.search(
        r'CACHED_FILES = (\[[^\]]*?\])', service_worker).group(1)
    cache_list_json = cache_list.replace("'", '"')
    cached_files = json.loads(cache_list_json)
    expected_cached_files = []
    for root, _, files in os.walk(self.output_path):
      for name in files:
        relpath = os.path.relpath(os.path.join(root, name), self.output_path)
        expected_cached_files.append(relpath)
    self.assertItemsEqual(cached_files, expected_cached_files)

  def test_polyfill_imports(self):
    """Tests that polyfills are imported."""
    chrome_app_manifest = {
      'app': {'background': {}}
    }
    polyfills = ['póly.polyfill.js', 'fill.polyfill.js']
    service_worker = caterpillar.generate_service_worker(
        self.output_path, chrome_app_manifest, polyfills, BOILERPLATE_DIR)
    for polyfill in polyfills:
      relpath = os.path.join(BOILERPLATE_DIR, polyfill)
      self.assertIn("importScripts('{}');".format(relpath), service_worker,
                    '{} not imported.'.format(relpath))

  def test_background_script_imports(self):
    """Tests that background scripts are imported."""
    chrome_app_manifest = {
      'app': {'background': {'scripts': ['my.jss', 'góod.aspx', 'script.py']}}
    }
    service_worker = caterpillar.generate_service_worker(
        self.output_path, chrome_app_manifest, [], BOILERPLATE_DIR)
    for script in chrome_app_manifest['app']['background']['scripts']:
      self.assertIn("importScripts('{}');".format(script), service_worker,
                    '{} not imported.'.format(script))


class TestAddServiceWorker(TestCaseWithOutputDir):
  """Tests add_service_worker."""

  def test_service_worker_added(self):
    """Tests that a service worker is added to the root of the PWA."""
    chrome_app_manifest = {
      'app': {'background': {}}
    }
    caterpillar.add_service_worker(
        self.output_path, chrome_app_manifest, [], BOILERPLATE_DIR)
    self.assertTrue(os.path.exists(os.path.join(self.output_path, 'sw.js')))


class TestEditCode(TestCaseWithOutputDir):
  """Tests edit_code."""

  def test_todos(self):
    """Tests that TODOs are inserted into JS files."""
    chrome_app_manifest = {
      'app': {'background': {}}
    }
    caterpillar.edit_code(self.output_path, [], chrome_app_manifest,
                          {'boilerplate_dir': BOILERPLATE_DIR})
    with codecs.open(os.path.join(self.output_path, 'my scrípt.js'),
                     encoding='utf-8') as js_file:
      self.assertEqual(js_file.read(),
"""// TODO(Caterpillar): Check usage of app.runtime.onLaunched.addListener.
chrome.app.runtime.onLaunched.addListener(function() {
// TODO(Caterpillar): Check usage of app.window.create.
  chrome.app.window.create('my índex.html');
});
""")

  def test_script_tags(self):
    """Tests that script tags are inserted into HTML files."""
    chrome_app_manifest = {
      'app': {'background': {}}
    }
    caterpillar.edit_code(self.output_path, ['tést.js'], chrome_app_manifest,
                          {'boilerplate_dir': BOILERPLATE_DIR})
    with codecs.open(os.path.join(self.output_path, 'my índex.html'),
                     encoding='utf-8') as js_file:
      self.assertIn(
          '<script src="{}"'.format(
              os.path.join('.', BOILERPLATE_DIR, 'tést.js')),
          js_file.read())

  def test_meta_tags(self):
    """Tests that meta tags are inserted into HTML files."""
    chrome_app_manifest = {
      'app': {'background': {}},
      'name': 'test233'
    }
    caterpillar.edit_code(self.output_path, [], chrome_app_manifest,
                          {'boilerplate_dir': BOILERPLATE_DIR})
    with codecs.open(os.path.join(self.output_path, 'my índex.html'),
                     encoding='utf-8') as js_file:
      self.assertIn('<meta content="test233" name="name"', js_file.read())


class TestAddAppInfo(TestCaseWithOutputDir):
  """Tests add_app_info."""

  def test_add_app_info(self):
    """Tests add_app_info writes the correct file."""
    chrome_app_manifest = {
      'app': {'background': {}},
      'name': 'tést app\'',
    }

    caterpillar.add_app_info(self.output_path, chrome_app_manifest)

    with open(os.path.join(self.output_path, 'app.info.js')) as app_info_file:
      app_info_js = app_info_file.read().decode('utf-8')

    self.assertEqual(app_info_js, """\
chrome.caterpillar.manifest = {
  "app": {
    "background": {}
  },
  "name": "t\\u00e9st app'"
};
""")


if __name__ == '__main__':
  unittest.main()
