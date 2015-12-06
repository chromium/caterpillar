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

"""Chrome App manifest verification and parsing.
"""

import json
import logging
import os

# Chrome App manifest filename.
MANIFEST_FILENAME = 'manifest.json'

def get(directory):
  """
  Returns a directory's manifest file as a dictionary.

  Args:
    directory: Path of directory the manifest is located in.

  Returns:
    Manifest file as a dictionary.

  Raises:
    IOError if the directory does not contain a manifest file.
    ValueError if the manifest file is invalid.
  """
  manifest_path = os.path.join(directory, MANIFEST_FILENAME)
  with open(manifest_path) as manifest_file:
    manifest = json.load(manifest_file)

  return manifest

def verify(manifest):
  """
  Verifies that the manifest is valid.

  Args:
    manifest: Manifest dictionary.

  Raises:
    ValueError if the manifest is invalid in a way that could break the
      converter.
  """
  # Manifests must have a version.
  if 'manifest_version' not in manifest:
    logging.warning('Chrome Apps must have manifest version 2.')
  else:
    logging.debug('Manifest has a manifest version.')
    # Manifests must be version 2.
    if manifest['manifest_version'] != 2:
      logging.warning('Chrome Apps must have manifest version 2, found manifest'
        ' version %s.', manifest['manifest_version'])
    else:
      logging.debug('Found manifest version 2.')


  # The app/background is required.
  if 'app' not in manifest or 'background' not in manifest['app']:
    raise ValueError('Chrome Apps must include a background script.')

  # The name is required.
  if 'name' not in manifest:
    logging.warning('Chrome Apps must include a name.')

  # The version is required.
  if 'version' not in manifest:
    logging.warning('Chrome Apps must include a version.')

  # Warn on manifest members that won't be converted.
  included = {'manifest_version', 'app', 'name', 'version', 'short_name',
    'default_locale', 'icons', 'author', 'description'}
  for member in manifest:
    if member not in included:
      logging.warning('Manifest member `%s` will not be converted.', member)
