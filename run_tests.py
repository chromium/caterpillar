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

"""Runs Caterpillar unit tests.

Tests can be run in several ways.

./run_tests.py
  Runs all tests.

./run_tests.py js
  Runs all JS tests.

./run_tests.py py
  Runs all Python tests.

./run_tests.py py module.submodule.TestCase
  Runs the tests in the given test case.
"""

import argparse
import os.path
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
KARMA_PATH = os.path.join(SCRIPT_DIR, 'node_modules', 'karma', 'bin', 'karma')
CATERPILLAR_TESTS_DIR = os.path.join(SCRIPT_DIR, 'src')


def run_all_js_tests():
  subprocess.call([KARMA_PATH, 'start'])


def run_all_py_tests():
  subprocess.call(['python', '-m', 'unittest', 'discover', '-s',
                   CATERPILLAR_TESTS_DIR, '-p', '*_test.py'])


def run_modules_py_tests(modules):
  for module in modules:
    subprocess.call(['python', '-m', 'unittest', module],
                    cwd=CATERPILLAR_TESTS_DIR)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('mode', choices=('all', 'js', 'py'), default='all',
                      nargs='?', help='Language to test.')
  parser.add_argument('modules', nargs='*', help='Modules to test (py only).')

  args = parser.parse_args()

  if args.mode == 'js' and args.modules:
    raise ValueError('Can\'t specify module with mode `js`.')

  if args.mode == 'all':
    run_all_js_tests()
    if not args.modules:
      run_all_py_tests()
    else:
      run_modules_py_tests(args.modules)
  elif args.mode == 'js':
    run_all_js_tests()
  elif args.modules:
    run_modules_py_tests(args.modules)
  else:
    run_all_py_tests()
