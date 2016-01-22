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

"""Utilities for walking a Chrome App and yielding information from it.
"""

import os


def all_paths(directory, extension=None):
  """Walks a directory and yields all the file paths, possibly filtering by file
  extension.

  Args:
    directory: Path to a directory.
    extension: File extension. Optional.

  Yields:
    File paths.
  """
  dirwalk = os.walk(directory)
  for (dirpath, _, filenames) in dirwalk:
    for filename in filenames:
      if extension is None or filename.lower().endswith('.' + extension):
        path = os.path.join(dirpath, filename)
        yield path
