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

"""Caterpillar presubmit checks."""

import os

TEST_DATA_REALPATHS = [
    os.path.realpath(os.path.join('tests', 'test_app_minimal')),
    os.path.realpath(os.path.join('tests', 'test_app_tts')),
    os.path.realpath(os.path.join('tests', 'test_app_tts_output')),
]

def filter_test_data(affected_file):
  path = affected_file.LocalPath()
  realpath = os.path.realpath(path)

  for test_path in TEST_DATA_REALPATHS:
    if realpath.startswith(test_path):
      return False

  return True

def CheckChange(input_api, output_api):
  results = []
  results += input_api.canned_checks.CheckChangeHasNoTabs(
      input_api, output_api)
  results += input_api.canned_checks.CheckChangeHasDescription(
      input_api, output_api)
  results += input_api.canned_checks.CheckChangeHasNoCrAndHasOnlyOneEol(
      input_api, output_api)
  results += input_api.canned_checks.CheckLongLines(input_api, output_api, 80,
      source_file_filter=filter_test_data)
  results += input_api.canned_checks.CheckChangeHasNoStrayWhitespace(
      input_api, output_api, source_file_filter=filter_test_data)
  results += input_api.RunTests(GetPythonTests(input_api, output_api))
  results += input_api.RunTests(GetKarmaTests(input_api, output_api))

  return results

def CheckChangeOnUpload(input_api, output_api):
  return CheckChange(input_api, output_api)

def CheckChangeOnCommit(input_api, output_api):
  return CheckChange(input_api, output_api)

def GetKarmaTests(input_api, output_api):
  cmd = [
      input_api.os_path.join('node_modules', 'karma', 'bin', 'karma'), 'start']
  return [input_api.Command('Karma', cmd, {}, output_api.PresubmitError)]

def GetPythonTests(input_api, output_api):
  command = ['python', '-m', 'unittest', 'discover', '-s', 'src/', '-p',
             '*_test.py']
  return [input_api.Command('Python', command, {}, output_api.PresubmitError)]
