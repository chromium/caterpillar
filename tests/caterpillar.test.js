// Copyright 2015 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @file Tests for the polyfill for Chrome Apps' runtime API.
 * @author alger@google.com
 */

'use strict';

// Test caterpillar loaded okay.
QUnit.test('caterpillar loaded', assert => {
  assert.ok('chrome' in window, 'found chrome');
  assert.ok('caterpillar' in chrome, 'found chrome.caterpillar');
});

QUnit.test('Message', assert => {
  var m = new chrome.caterpillar.Message(
    chrome.caterpillar.MessageType.NOTIFICATION, []);
  assert.equal(m.type, chrome.caterpillar.MessageType.NOTIFICATION);
  assert.deepEqual(m.args, []);
  assert.equal(m.toString(), 'chrome.caterpillar.Message(notification, [...])');
});

QUnit.test('setError sets an error if runtime is loaded', assert => {
  if (!chrome.runtime)
    chrome.runtime = {};

  chrome.runtime.lastError = null;
  chrome.caterpillar.setError('error message');
  assert.deepEqual(chrome.runtime.lastError,
    { 'message': 'error message' });
  delete chrome.runtime.lastError;
});