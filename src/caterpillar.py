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

"""Semi-automatically convert Chrome Apps into progressive web apps.

Guides a developer through converting their existing Chrome App into a
progressive web app.
"""

from __future__ import print_function, division, unicode_literals

import argparse
import json
import logging
import os
import shutil
import sys

import bs4

import chrome_apis
import chrome_app.manifest

# Chrome APIs with polyfills available.
POLYFILLS = {
}

# What the converter is called.
CONVERTER_NAME = 'caterpillar'

# Where this file is located (so we can find resources).
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def setup_output_dir(input_dir, output_dir, force=False):
  """
  Sets up the output directory tree.

  Copies all files from the input directory to the output directory, and creates
  a subdirectory for the boilerplate code.

  Args:
    input_dir: String path to input directory.
    output_dir: String path to output directory.
    force: Whether to force overwrite existing output files. Default is False.

  Raises:
    ValueError: Invalid input or output directory.
  """
  if force:
    logging.debug('Removing output directory tree `%s`.', output_dir)
    shutil.rmtree(output_dir, ignore_errors=True)
  elif os.path.exists(output_dir):
    raise ValueError('Output directory already exists.')

  logging.debug('Copying input tree `%s` to output tree `%s`.', input_dir,
                output_dir)
  shutil.copytree(input_dir, output_dir)
  conv_path = boilerplate_dir(output_dir)
  logging.debug('Making %s directory `%s`.', CONVERTER_NAME, conv_path)
  os.mkdir(conv_path)
  logging.debug('Finished setting up output directory `%s`.', output_dir)

def polyfill_apis(apis, directory):
  """
  Copies polyfill scripts into a directory.

  Args:
    apis: List of APIs to polyfill. Strings e.g. 'tts' for the chrome.tts API.
    directory: Directory name to copy into.

  Returns:
    (sorted list of successfully polyfilled APIs,
     sorted list of unsuccessfully polyfilled APIs)
  """
  successful = []
  unsuccessful = []

  for api in apis:
    if api not in POLYFILLS:
      unsuccessful.append(api)
      continue

    polyfill_filename = '{}.polyfill.js'.format(api)
    polyfill_path = os.path.join(SCRIPT_DIR, 'js', 'polyfills',
                                 polyfill_filename)
    destination_path = os.path.join(directory, polyfill_filename)
    shutil.copyfile(polyfill_path, destination_path)
    successful.append(api)

  successful.sort()
  unsuccessful.sort()
  return (successful, unsuccessful)

def ca_to_pwa_manifest(manifest, config):
  """
  Converts a Chrome App manifest into a progressive web app manifest.

  Args:
    manifest: Manifest dictionary.
    config: Conversion configuration dictionary.

  Returns:
    PWA manifest.
  """
  pwa_manifest = {}
  pwa_manifest['name'] = manifest['name']
  pwa_manifest['short_name'] = manifest.get('short_name', manifest['name'])
  pwa_manifest['lang'] = manifest.get('default_locale', 'en')
  pwa_manifest['splash_screens'] = []
  # TODO(alger): Guess display mode from chrome.app.window.create calls
  pwa_manifest['display'] = 'minimal-ui'
  pwa_manifest['orientation'] = 'any'
  # TODO(alger): Guess start_url from chrome.app.window.create calls
  pwa_manifest['start_url'] = config['start_url']
  # TODO(alger): Guess background/theme colour from the main page's CSS.
  pwa_manifest['theme_color'] = 'white'
  pwa_manifest['background_color'] = 'white'
  pwa_manifest['related_applications'] = []
  pwa_manifest['prefer_related_applications'] = False
  pwa_manifest['icons'] = []
  if 'icons' in manifest:
    for icon_size in manifest['icons']:
      pwa_manifest['icons'].append({
        'src': manifest['icons'][icon_size],
        'sizes': '{0}x{0}'.format(icon_size)
      })

  # TODO(alger): I've only looked at some of the manifest members here; probably
  # a bad idea to ignore the ones that don't copy across. Should give a warning.

  return pwa_manifest

def boilerplate_dir(directory):
  """
  Gets the path to the converter's boilerplate directory.

  Args:
    directory: Directory path of app.

  Returns:
    Path to boilerplate directory within the given directory.
  """
  return os.path.join(directory, CONVERTER_NAME)

def relative_boilerplate_file_path(filename):
  """
  Gets the path to a boilerplate file relative to the app root.

  Example:
    relative_boilerplate_file_path('tts.polyfill.js')
      == 'caterpillar/tts.polyfill.js'

  Args:
    filename: Filename of the resource to get the path of.

  Returns:
    Path to the file within the boilerplate directory, relative to the app root.
  """
  return '{}/{}'.format(CONVERTER_NAME, filename)

def convert_app(input_dir, output_dir, config, force=False):
  """
  Converts a Chrome App into a progressive web app.

  Args:
    input_dir: String path to input directory.
    output_dir: String path to output directory.
    config: Configuration dictionary.
    force: Whether to force overwrite existing output files. Default is False.
  """
  # Copy everything across to the output directory.
  try:
    setup_output_dir(input_dir, output_dir, force)
  except ValueError as e:
    logging.error(e.message)
    return

  # Initial pass to detect and polyfill Chrome Apps APIs.
  apis = chrome_apis.app_apis(output_dir)
  if apis:
    logging.info('Found Chrome APIs: %s', ', '.join(apis))

  conv_dir = boilerplate_dir(output_dir)
  successful, unsuccessful = polyfill_apis(apis, conv_dir)
  if successful:
    logging.info('Polyfilled Chrome APIs: %s', ', '.join(successful))
  if unsuccessful:
    logging.warning(
      'Could not polyfill Chrome APIs: %s', ', '.join(unsuccessful))

  # Read in and check the manifest file. Generate the new manifest from that.
  try:
    manifest = chrome_app.manifest.get(output_dir)
  except ValueError as e:
    logging.error(e.message)
    return

  try:
    chrome_app.manifest.verify(manifest)
  except ValueError as e:
    logging.error(e.message)
    return

  # Convert the Chrome app manifest into a progressive web app manifest.
  pwa_manifest = ca_to_pwa_manifest(manifest, config)
  pwa_manifest_path = os.path.join(output_dir, 'manifest.json')
  with open(pwa_manifest_path, 'w') as pwa_manifest_file:
    json.dump(pwa_manifest, pwa_manifest_file, indent=4, sort_keys=True)
  logging.debug('Wrote `manifest.json` to `%s`.', pwa_manifest_path)

  # TODO(alger): Inject tags into the HTML of the start file and write the HTML
  # back to the output directory.
  # TODO(alger): Copy service worker scripts.

  logging.info('Conversion complete.')

def main():
  desc = 'Semi-automatically convert Chrome Apps into progressive web apps.'
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('-c', '--config', help='Configuration file',
                      required=True, metavar='config')
  parser.add_argument('-i', '--input', help='Chrome App input directory',
                      required=True, metavar='input')
  parser.add_argument('-o', '--output',
                      help='Progressive web app output directory',
                      required=True, metavar='output')
  parser.add_argument('-v', '--verbose', help='Verbose logging',
                      action='store_true')
  parser.add_argument('-f', '--force', help='Force output overwrite',
                      action='store_true')
  args = parser.parse_args()

  if args.verbose:
    logging_level = logging.DEBUG
  else:
    logging_level = logging.INFO
  logging_format = ':%(levelname)s:  \t%(message)s'
  logging.basicConfig(level=logging_level, format=logging_format)

  with open(args.config) as config_file:
    config = json.load(config_file)

  convert_app(args.input, args.output, config, args.force)

if __name__ == '__main__':
  sys.exit(main())