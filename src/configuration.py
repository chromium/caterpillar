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

"""Handles configuration options for Caterpillar.

This includes inputting of the config file and generating new config files.
"""

from __future__ import print_function, division, unicode_literals

import json
import logging

import surrogateescape

# Names of the configuration options mapped to a brief description and a default
# value.
OPTIONS = {
  'id': ('Chrome App ID', '-1'),
  'start_url': ('Path to main HTML file', 'index.html'),
  'root': ('Where the root of the web app will be', '.'),
  'boilerplate_dir':
    ('Subdirectory of root where Caterpillar will put scripts', 'caterpillar'),
  'update_uris':
    ('Whether to normalise all URIs in the web app to the root', True),
  'report_dir': ('Directory of generated output report', 'caterpillar-report'),
}


def str_to_bool(string):
  """Converts a case-insensitive string 'true' or 'false' into a bool.

  Args:
    string: String to convert. Either 'true' or 'false', case-insensitive.

  Raises:
    ValueError if string is not 'true' or 'false'.
  """
  lower_string = string.lower()

  if lower_string == 'true':
    return True

  if lower_string == 'false':
    return False

  raise ValueError('Expected "true" or "false"; got "{}".'.format(string))


def generate(interactive=False):
  """Generate a configuration file.

  Args:
    interactive: True iff the user should be prompted to choose their own config
      options, as opposed to automatically using the defaults.

  Returns:
    Configuration dictionary

  Raises:
    ValueError when a non-Boolean value is given for an option expected to be
      Boolean.
  """
  config = {}
  for opt, (desc, default) in sorted(OPTIONS.items()):
    config[opt] = default

    if interactive:
      value = raw_input('{} ({}): '.format(desc, default))

      if not value:
        continue

      if isinstance(default, bool):
        value = str_to_bool(value)

      config[opt] = value

  return config


def load(config_path):
  """Loads a JSON configuration file.

  Warns if the config file is missing or has unexpected options.

  Args:
    config_path: Path to a JSON configuration file.

  Returns:
    Configuration dictionary

  Raises:
    IOError if the config file is not found.
    ValueError if the config file is not valid JSON.
  """
  with open(config_path) as config_file:
    config = json.load(config_file)

  missing = missing_options(config)
  if missing:
    logging.warning('Configuration file `%s` missing options: %s', config_path,
                    ', '.join(missing))

  unexpected = unexpected_options(config)
  if unexpected:
    logging.warning('Configuration file `%s` has unexpected options: %s',
                    config_path, ', '.join(unexpected))

  return config


def missing_options(config):
  """Returns a list of expected options missing from a configuration dictionary.

  Args:
    config: Configuration dictionary

  Returns:
    List of missing option names
  """
  return sorted(opt for opt in OPTIONS if opt not in config)


def unexpected_options(config):
  """Returns a list of unexpected options found in a configuration dictionary.

  Args:
    config: Configuration dictionary

  Returns:
    List of unexpected option names
  """
  return sorted(opt for opt in config if opt not in OPTIONS)


def generate_and_save(output_path, interactive=False):
  """Generates and outputs a configuration file.

  Args:
    output_path: Path to save config file to.
    interactive: True iff generating the config should use user input.
  """
  config = generate(interactive)
  with open(output_path, 'w') as output_file:
    json.dump(config, output_file, sort_keys=True, indent=2)
