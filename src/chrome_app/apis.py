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

"""Checks what Chrome APIs Chrome Apps are using.

Exports a function to walk an app directory and return a set of all Chrome
APIs used, and a function to walk a directory containing multiple apps and
return a list of (app name, app dir, API set) tuples. This is a pretty naive
check; there are no guarantees that all APIs will be found.

Can also be used from the command line.
"""

from __future__ import print_function, division, unicode_literals

import argparse
import json
import logging
import re
import os
import sys

import manifest as app_manifest

# Regular expression matching Chrome API namespaces, e.g. chrome.tts and
# chrome.app.window.
CHROME_API_REGEX = re.compile(
  r'(?<![\w.])chrome\.((?:(?:app|sockets|system)\.)?\w+)')

# Regular expression matching Chrome apps API usage, e.g.
# chrome.tts.speak and chrome.app.runtime.onLaunched.addListener.
CHROME_API_USAGE_REGEX = re.compile(r'(?<![\w.])chrome\.((?:\w+\.)+\w+)')

def api_member_used(line):
  """
  Checks if a line of code uses a Chrome Apps API and returns the used member
  name if applicable.

  Args:
    line: String line of code.

  Returns:
    None or string member name.
  """
  use_match = CHROME_API_USAGE_REGEX.search(line)
  if not use_match:
    return None

  return use_match.group(1)

def app_apis(directory):
  """Returns a set of Chrome APIs used in a given app directory.

  Args:
    directory: App directory to search for Chrome APIs.

  Returns:
    A sorted list of Chrome API names.
  """
  # This will be done really naively by searching for 'chrome.*'.
  # Note that this fails for cases like 'var a = chrome; a.tts;'.

  # For each js file in the directory, add all of the Chrome APIs being used to
  # a set of Chrome API names.
  dirwalk = os.walk(directory)
  apis = set()
  for (dirpath, _, filenames) in dirwalk:
    for filename in filenames:
      if filename.endswith('.js'):
        path = os.path.join(dirpath, filename)
        with open(path) as js_file:
          js = js_file.read()
          for api_match in CHROME_API_REGEX.finditer(js):
            apis.add(api_match.group(1))

  return sorted(apis)

def apps_apis(directory):
  """Finds Chrome APIs used by each app in a directory of apps.

  Args:
    directory: Directory containing many app directories.

  Yields:
    (app name, app dir, API set)
  """
  apps = os.listdir(directory)
  apps.sort()
  for app in apps:
    path = os.path.join(directory, app)
    if os.path.isdir(path):
      try:
        manifest = app_manifest.get(path)
      except IOError:
        # No manifest.
        continue
      except ValueError:
        # Invalid manifest.
        logging.warn('Invalid manifest found in app `%s`; skipping.', path)
        continue

      name = manifest['name']
      apis = app_apis(path)
      yield (name, path, apis)

def main():
  """Parses command line arguments and scans APIs based on these arguments.
  """
  parser = argparse.ArgumentParser(description='Check what Chrome APIs Chrome '
    'Apps are using.')
  parser.add_argument('directory')
  parser.add_argument('-m', '--multiple', help='Check multiple apps',
    action='store_true')
  parser.add_argument('-v', '--verbose', help='Verbose output',
    action='store_true')
  args = parser.parse_args()

  if args.verbose:
    logging_level = logging.DEBUG
  else:
    logging_level = logging.INFO

  logging_format = ':%(levelname)s:  \t%(message)s'
  logging.basicConfig(level=logging_level, format=logging_format)

  if args.multiple:
    info = apps_apis(args.directory)
    for name, path, apis in info:
      print("{} ({}): {}".format(name, path, ", ".join(apis)))
  else:
    apis = app_apis(args.directory)
    print(", ".join(apis))

if __name__ == '__main__':
  sys.exit(main())
