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
 * Tests for Caterpillar common code.
 */

'use strict';

QUnit.test('setError sets an error', assert => {
  chrome.runtime.lastError = null;
  caterpillar_.setError('error message');
  assert.deepEqual(chrome.runtime.lastError,
    { 'message': 'error message' });
  delete chrome.runtime.lastError;
});

QUnit.test('chrome namespace is defined', assert => {
  assert.ok('chrome' in self);
});

QUnit.test('caterpillar_ namespace is defined', assert => {
  assert.ok('caterpillar_' in self);
});

QUnit.test('chrome.runtime namespace is defined', assert => {
  assert.ok('runtime' in chrome);
});

QUnit.test('chrome.app.runtime.onLaunched.addListener is stubbed', assert => {
  assert.expect(0);
  chrome.app.runtime.onLaunched.addListener(function() {});
});

QUnit.test('Appropriate web functions are disabled', assert => {
  assert.throws(alert,
      new Error('alert() is not available in converted apps.'));
  assert.throws(confirm,
      new Error('confirm() is not available in converted apps.'));
  assert.throws(document.close,
      new Error('document.close() is not available in converted apps.'));
  assert.throws(document.open,
      new Error('document.open() is not available in converted apps.'));
  assert.throws(document.write,
      new Error('document.write() is not available in converted apps.'));
  assert.throws(showModalDialog,
      new Error('showModalDialog() is not available in converted apps.'));
});

QUnit.test('localStorage disabled', assert => {
  assert.notOk('localStorage' in self);
});
