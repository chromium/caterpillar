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

"""Implements Python 3's 'surrogateescape' Unicode error handling scheme. This
allows byte strings with unknown ASCII-compatible encoding to be decoded into
Unicode strings, manipulated as such, and encoded back to byte strings
losslessly.
"""

from __future__ import print_function, division, unicode_literals

import codecs


def error_handler(error):
  """Error handler for surrogateescape decoding.

  Should be used with an ASCII-compatible encoding (e.g., 'latin-1' or 'utf-8').
  Replaces any invalid byte sequences with surrogate code points.

  As specified in
  https://docs.python.org/2/library/codecs.html#codecs.register_error.
  """
  # We can't use this with UnicodeEncodeError; the UTF-8 encoder doesn't raise
  # an error for surrogates. Instead, use encode.
  if not isinstance(error, UnicodeDecodeError):
    raise error

  result = []
  for i in range(error.start, error.end):
    byte = ord(error.object[i])
    if byte < 128:
      raise error
    result.append(unichr(0xdc00 + byte))

  return ''.join(result), error.end


def decode(bytestring, encoding='utf-8'):
  """Decoder for 'surrogateescape'.

  Args:
    bytestring: Byte string to be decoded.

  Returns:
    Unicode string, with surrogate control points for any byte value that could
    not be decoded with the given encoding.
  """
  return bytestring.decode(encoding, errors='surrogateescape')


def encode(string, encoding='utf-8'):
  """Encoder for 'surrogateescape'.

  Args:
    string: Unicode string to be encoded.

  Returns:
    Byte string, with any surrogate control points from the input string being
    converted back into the original byte value.
  """
  # Can't use str.encode due to technical limitations in Python 2.
  result = []
  for char in string:
    cp = ord(char)
    if 0xdc00 <= cp < 0xdd00:
      result.append(chr(cp - 0xdc00))
    else:
      result.append(char.encode(encoding))
  return b''.join(result)


def make_printable(string):
  """Makes a surrogate-escaped string printable.

  Args:
    string: Unicode string with surrogate code points.

  Returns:
    Unicode string having surrogates replaced by the replacement character.
  """
  return ''.join('\ufffd' if 0xd800 <= ord(c) < 0xe000 else c for c in string)


try:
  codecs.lookup_error('surrogateescape')
except LookupError:
  codecs.register_error('surrogateescape', error_handler)
