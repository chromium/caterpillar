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

"""Utilities for reading polyfill metadata."""

from __future__ import print_function, division, unicode_literals

import json
import os

# Where this file is located (so we can find resources).
SCRIPT_DIR = os.path.dirname(__file__)


def default(api):
  """Generates a default manifest for a given API.

  Args:
    api: API name.

  Returns:
    Default polyfill manifest dictionary.
  """
  return {
    'name': api,
    'status': 'none',
    'coverage': 0.00,
    'dependencies': [],
    'warnings': [],
  }


def load(api):
  """Loads the polyfill manifests for the given API.

  Args:
    api: API name.

  Returns:
    Polyfill manifest dictionary.
  """
  manifest_path = os.path.join(
      SCRIPT_DIR, 'js', 'polyfills', '{}.manifest.json'.format(api))
  with open(manifest_path) as manifest_file:
    manifest = json.load(manifest_file)
    return manifest


def load_many(apis):
  """Loads the polyfill manifests for the given APIs.

  Args:
    apis: List of API names.

  Returns:
    Dictionary mapping API names to polyfill manifest dictionaries.
  """
  manifests = {}
  for api in apis:
    manifests[api] = load(api)

  return manifests
