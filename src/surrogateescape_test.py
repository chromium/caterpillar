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

from __future__ import print_function, division, unicode_literals

import unittest

import surrogateescape


class SurrogateEscapeTest(unittest.TestCase):

  def testSurrogateDecode(self):
    bs = b'latin-1: caf\xe9; utf-8: caf\xc3\xa9'
    s = bs.decode('utf-8', errors='surrogateescape')
    self.assertIsInstance(s, unicode)
    self.assertEqual(s, u'latin-1: caf\udce9; utf-8: caf\xe9')

    s = surrogateescape.decode(bs)
    self.assertIsInstance(s, unicode)
    self.assertEqual(s, u'latin-1: caf\udce9; utf-8: caf\xe9')

  def testSurrogateEncode(self):
    s = u'latin-1: caf\udce9; utf-8: caf\xe9'
    bs = surrogateescape.encode(s)
    self.assertIsInstance(bs, bytes)
    self.assertEqual(bs, b'latin-1: caf\xe9; utf-8: caf\xc3\xa9')

  def testMakePrintable(self):
    s = u'latin-1: caf\udce9; utf-8: caf\xe9'
    printable = surrogateescape.make_printable(s)
    self.assertIsInstance(printable, unicode)
    self.assertEqual(printable, u'latin-1: caf\ufffd; utf-8: caf\xe9')


if __name__ == '__main__':
  unittest.main()
