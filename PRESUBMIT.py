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

TESTS = [
  'src/caterpillar_test.py'
]

def CheckChange(input_api, output_api):
  results = []
  results += input_api.canned_checks.CheckChangeHasNoTabs(
    input_api, output_api)
  results += input_api.canned_checks.CheckChangeHasDescription(
    input_api, output_api)
  results += input_api.canned_checks.CheckLongLines(input_api, output_api, 80)
  results += input_api.canned_checks.CheckChangeHasNoCrAndHasOnlyOneEol(
    input_api, output_api)
  results += input_api.canned_checks.CheckChangeHasNoStrayWhitespace(
    input_api, output_api)
  results += input_api.RunTests(
    input_api.canned_checks.GetUnitTests(input_api, output_api, TESTS))
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
