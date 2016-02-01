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
 * Tests for the polyfill for Chrome Apps' runtime API.
 */

'use strict';

QUnit.module('runtime');

// Test getBackgroundPage puts an error into chrome.runtime.lastError (since
// there is no background page).
QUnit.test('getBackgroundPage errors', function (assert) {
  var done = assert.async();
  chrome.runtime.lastError = null;
  chrome.runtime.getBackgroundPage(function(e) {
    assert.deepEqual(chrome.runtime.lastError,
        {'message': 'No background page for progressive web apps.'});
    done();
  });
});

// Test openOptionsPage puts an error into chrome.runtime.lastError (since
// there is no options page).
QUnit.test('openOptionsPage errors', function (assert) {
  var done = assert.async();
  chrome.runtime.lastError = null;
  chrome.runtime.openOptionsPage(function(e) {
    assert.deepEqual(chrome.runtime.lastError,
        {'message': 'Could not create an options page.'});
    done();
  });
});

// Test getManifest gets the manifest.
// Uses the test application's app.info.js file.
QUnit.test('getManifest gets manifest', function (assert) {
  var manifest = chrome.runtime.getManifest();
  assert.deepEqual(manifest, { 'name': 'test' });
});

// Test setUninstallURL. This function does nothing but the callback should be
// called nevertheless.
QUnit.test('setUninstallURL calls callback', function (assert) {
  assert.expect(0);
  var done = assert.async();
  var callback = done;
  chrome.runtime.setUninstallURL('', callback);
});

// reload would be tested here, but you can't stub window.reload.

// Test requestUpdateCheck returns NO_UPDATE.
QUnit.test('requestUpdateCheck returns NO_UPDATE', function (assert) {
  var done = assert.async();
  chrome.runtime.requestUpdateCheck(function(status, details) {
    assert.equal(status, chrome.runtime.RequestUpdateCheckStatus.NO_UPDATE);
    assert.strictEqual(details, undefined, 'no details');
    done();
  });
});

// Check that Port-related functions throw not implemented errors.
QUnit.test('connect not implemented', function (assert) {
  assert.throws(chrome.runtime.connect, 'not implemented');
});

QUnit.test('connectNative not implemented', function (assert) {
  assert.throws(chrome.runtime.connectŃative, 'not implemented');
});

// Check that getPlatformInfo calls the callback on the platform info.
QUnit.test('getPlatformInfo gets info', function (assert) {
  var done = assert.async();
  var originalOs = platform.os; // Test property.
  platform.os = {
    'family': 'LiNuX',
    'architecture': '32'
  };
  var callback = function(info) {
    assert.equal(info.os, chrome.runtime.PlatformOs.LINUX, 'correct OS');
    assert.equal(info.arch, chrome.runtime.PlatformArch.X86_32, 'correct arch');
    assert.equal(info.nacl_arch, chrome.runtime.PlatformNaclArch.X86_32,
                 'correct native arch');
    platform.os = originalOs;
    done();
  }

  chrome.runtime.getPlatformInfo(callback);
});

// Check that getPackageDirectoryEntry throws a not implemented error.
QUnit.test('getPackageDirectoryEntry not implemented', function(assert) {
  assert.throws(chrome.runtime.getPackageDirectoryEntry, 'not implemented');
});

// Test that id is null.
QUnit.test('id correct', function(assert) {
  assert.strictEqual(chrome.runtime.id, null);
});
