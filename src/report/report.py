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

"""Generates a Caterpillar conversion report.
"""

from __future__ import print_function, division, unicode_literals

import cgi
import copy
import logging
import os
import re
import shutil

import caterpillar
import chrome_app.apis
import polyfill_manifest
import surrogateescape
import templates

# Where this file is located (so we can find resources).
SCRIPT_DIR = os.path.dirname(__file__)


class Status(object):
  """Caterpillar conversion status constants."""

  NONE = 'none'
  PARTIAL = 'partial'
  TOTAL = 'total'


def generate_summary(chrome_app_manifest, apis, status, warnings):
  """Generates the summary section of a conversion report.

  Args:
    chrome_app_manifest: Manifest dictionary of input Chrome App.
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries.
    status: Status representing conversion status of the entire app.
    warnings: List of HTML general warnings logged during conversion.

  Returns:
    HTML
  """
  return templates.TEMPLATE_SUMMARY.render(
    chrome_app_manifest=chrome_app_manifest,
    apis=apis,
    status=status,
    warnings=warnings,
    Status=Status
  )


def generate_general_warnings(warnings):
  """Generates the general warnings section of a conversion report.

  Args:
    warnings: List of HTML general warnings logged during conversion.

  Returns:
    HTML
  """
  return templates.TEMPLATE_GENERAL_WARNINGS.render(warnings=warnings)


def process_usage(apis, usage):
  """Populates usage element of an API dictionary with the usages of that API.

  Args:
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries. This will be modified.
    usage: Usage dictionary mapping API names to
      (filepath, linenum, context, context_linenum) tuples.
  """

  for api_name, api_info in apis.iteritems():
    api_info['usage'] = []
    for uses in usage[api_name].values():
      for filepath, line_num, context, start in uses:
        context = cgi.escape(context)
        context = highlight_relevant_line(context, line_num - start, apis)
        api_info['usage'].append((filepath, line_num, context, start))

    # Sort first by file, then by line number.
    api_info['usage'].sort()


def generate_polyfilled(chrome_app_manifest, apis, web_path, ignore_dirs):
  """Generates the polyfilled section of a conversion report.

  Args:
    chrome_app_manifest: Manifest dictionary of input Chrome App.
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries.
    web_path: Path to output web app directory.
    ignore_dirs: Absolute directory paths to ignore for API usage.

  Returns:
    HTML
  """
  # Which APIs did we polyfill?
  polyfilled_apis = {api_name: api_info
                     for api_name, api_info in apis.iteritems()
                     if api_info['status'] != Status.NONE}

  usage = chrome_app.apis.usage(
      polyfilled_apis, web_path, ignore_dirs=ignore_dirs)

  process_usage(polyfilled_apis, usage)

  # Get the warnings for each API; split them into relevant and other warnings.
  for api_name, api_info in polyfilled_apis.iteritems():
    api_info['relevant_warnings'] = []
    api_info['other_warnings'] = []
    for warning in manifest_warnings(api_info, apis):
      # Is this warning's member used by the app?
      # Is it the parent of a member used by the app?
      for used_member in usage[api_name]:
        if used_member.startswith(warning['member']):
          # This test can and will match too many things, but I'd rather see a
          # warning which might not be relevant to my code than miss a warning
          # that might be.
          api_info['relevant_warnings'].append(warning['text'])
          break
      else:
        api_info['other_warnings'].append(warning['text'])

  return templates.TEMPLATE_POLYFILLED.render(
    some_polyfilled=bool(polyfilled_apis),
    apis=polyfilled_apis,
    chrome_app_manifest=chrome_app_manifest,
    Status=Status
  )


def highlight_relevant_line(context, relevant_line, apis):
  """Highlights the line in a usage context that is relevant.

  Args:
    context: Usage context string.
    relevant_line: Line within the context string we wish to highlight.
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries.

  Returns:
    Usage context string with highlighted relevant line.
  """
  lines = list(context.split('\n'))
  lines[relevant_line] = format_html(lines[relevant_line], apis)
  context = '\n'.join(lines)
  return context


def generate_not_polyfilled(chrome_app_manifest, apis, web_path, ignore_dirs):
  """Generates the missing polyfills section of a conversion report.

  Args:
    chrome_app_manifest: Manifest dictionary of input Chrome App.
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries.
    web_path: Path to output web app directory.
    ignore_dirs: Absolute directory paths to ignore for API usage.

  Returns:
    HTML
  """
  # Which APIs didn't we polyfill?
  missing_apis = {api: apis[api] for api in apis
                     if apis[api]['status'] == Status.NONE}

  usage = chrome_app.apis.usage(
      missing_apis, web_path, ignore_dirs=ignore_dirs)

  process_usage(missing_apis, usage)

  return templates.TEMPLATE_NOT_POLYFILLED.render(
    some_not_polyfilled=bool(missing_apis),
    apis=missing_apis,
    chrome_app_manifest=chrome_app_manifest,
    Status=Status
  )


def make_warning(name, member, text, apis):
  """Generates a warning dictionary.

  Args:
    name: Name of Chrome Apps API, e.g. tts for chrome.tts
    member: Member within Chrome Apps API, e.g. onChanged.addListener for
      chrome.storage.onChanged.addListener
    text: Text of warning.
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries.

  Returns:
    Warning dictionary of form {'member': member name e.g onChanged.addListener,
    'text': warning text}.
  """
  full_text = 'chrome.{}.{}: {}'.format(name, member, text)
  formatted_text = format_html(full_text, apis)

  return {'member': member, 'text': formatted_text}


def manifest_warnings(manifest, apis):
  """Extracts formatted warnings from a polyfill manifest.

  Args:
    manifest: Polyfill manifest dictionary.
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries.

  Returns:
    List of warning dictionaries, of the form {'member': member name, 'text':
    full warning text}.
  """
  warnings = []
  for warning in manifest['warnings']:
    # Warnings can be either strings, objects containing a string, or objects
    # containing a list of strings.
    if isinstance(warning, basestring):
      warnings.append(make_warning(manifest['name'], warning,
        'Not implemented in the polyfill.', apis))
    elif isinstance(warning['text'], basestring):
      warnings.append(make_warning(manifest['name'], warning['member'],
                                   warning['text'], apis))
    else:
      for text in warning['text']:
        warnings.append(make_warning(manifest['name'], warning['member'],
                                     text, apis))

  return warnings


def format_html(string, apis):
  """Formats a string as HTML, highlighting Chrome Apps APIs based on status.

  Args:
    string: String to format.
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries.

  Returns:
    Formatted HTML string
  """
  def replacer(match):
    # The match will be of the form chrome.a.b.c.d. We want to find the deepest
    # member with an independent status and set the status of the whole match
    # to that.
    match_group = match.group(1)[1:]  # Slice off the leading dot.
    if ('.' not in match_group or
        (match_group.count('.') == 1 and
         match_group.split('.', 1)[0] in {'app', 'sockets', 'system'})):
      # This match is either a standalone API (chrome.api) or a special
      # standalone API (chrome.superapi.api) and we can just take the top-level
      # status of the API.
      api = match_group
      status = apis[api]['status']
      return '<span class="ca-feature {}">{}</span>'.format(
          status, match.group(0))

    api, member = chrome_app.apis.CHROME_API_AND_MEMBER_REGEX.match(
      match.group(0)).groups()

    status = None
    while True:
      # Check if the member has a status; if it does, use that, otherwise jump
      # to the parent member.
      for warning in apis[api]['warnings']:
        if member == warning:
          status = Status.NONE
          break

        try:
          warning_member = warning['member']
        except TypeError:  # This is a string warning for a different member.
          continue

        if warning_member == member:
          status = warning['status']
          break

      if status is not None:
        break

      if '.' not in member:
        status = apis[api]['status']
        break

      member = member.rsplit('.', 1)[0]

    return '<span class="ca-feature {}">{}</span>'.format(
        status, match.group(0))

  return chrome_app.apis.CHROME_NAMESPACE_REGEX.sub(replacer, string)


def generate(chrome_app_manifest, apis, status, warnings, web_path,
             boilerplate_dir):
  """Generates a conversion report.

  Args:
    chrome_app_manifest: Manifest dictionary of input Chrome App.
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries.
    status: Status representing conversion status of the entire app.
    warnings: List of general warnings logged during conversion.
    web_path: Path to output progressive web app.
    boilerplate_dir: Boilerplate directory relative to the output directory.

  Returns:
    HTML
  """
  # Ignore the Caterpillar boilerplate directory so we don't see polyfill code
  # included in API usages.
  ignore_dirs = {os.path.abspath(os.path.join(web_path, boilerplate_dir))}

  warnings = [format_html(warning, apis) for warning in warnings]
  summary = generate_summary(chrome_app_manifest, apis, status, warnings)
  general_warnings = generate_general_warnings(warnings)
  polyfilled = generate_polyfilled(
      chrome_app_manifest, apis, web_path,ignore_dirs)
  not_polyfilled = generate_not_polyfilled(
      chrome_app_manifest, apis, web_path, ignore_dirs)
  return templates.TEMPLATE_FULL.render(
    chrome_app_manifest=chrome_app_manifest,
    summary=summary,
    general_warnings=general_warnings,
    polyfilled=polyfilled,
    not_polyfilled=not_polyfilled
  )


def copy_css(directory):
  """Copies required report CSS into a directory.

  Args:
    directory: Directory to copy CSS into.
  """
  logging.debug('Copying CSS into directory `%s`', directory)
  shutil.copyfile(os.path.join(SCRIPT_DIR, 'report.css'),
                  os.path.join(directory, 'report.css'))


def install_bower_dependencies(dependencies, directory):
  """Installs bower dependencies into a directory.

  Args:
    dependencies: List of dependency names.
    directory: Directory to install dependencies into.
  """
  for dependency in dependencies:
    caterpillar.install_dependency(['bower', 'install', dependency], directory)


def generate_and_write(report_dir, chrome_app_manifest, apis, status, warnings,
                       pwa_path):
  """Generates a conversion report and writes it to a directory.

  Args:
    report_dir: Directory to write report to.
    chrome_app_manifest: Manifest dictionary of input Chrome App.
    apis: Dictionary mapping Chrome Apps API name to polyfill manifest
      dictionaries.
    status: Status representing conversion status of the entire app.
    warnings: List of general warnings logged during conversion.
    pwa_path: Path to output progressive web app.
  """
  report = generate(chrome_app_manifest, apis, status, warnings, pwa_path)
  report_path = os.path.join(report_dir, 'report.html')
  with open(report_path, 'w') as report_file:
    logging.info('Writing conversion report to `%s`.', report_path)
    report_file.write(surrogateescape.encode(report))
  copy_css(report_dir)
  install_bower_dependencies(['lato', 'inconsolata', 'code-prettify'],
                             report_dir)
