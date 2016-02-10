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
 * Common utilities and namespaces for Caterpillar.
 *
 * Must be included before any Caterpillar polyfills.
 */

(function() {

'use strict';

// Set up a namespace for the polyfills if one doesn't already exist.
if (!('chrome' in self))
  self.chrome = {};

if (!('caterpillar_' in self))
  self.caterpillar_ = {};

// We need the chrome.runtime namespace to store errors in.
if (!chrome.runtime)
  chrome.runtime = { lastError: null };

// Stub out chrome.app.runtime.onLaunched.addListener. All Chrome Apps call this
// method to launch the main window. Stubbing it means that background scripts
// that launch the main window can be re-used elsewhere without causing script
// errors.

// chrome.app is always defined in Chrome, and Chrome will overwrite it if it is
// replaced outright.
if (!chrome.app)
  chrome.app = {};

if (!chrome.app.runtime) {
  chrome.app.runtime = {
    onLaunched: {
      addListener: function() {},
    }
  };
}

/**
 * Sets an error message in chrome.runtime.lastError.
 *
 * @param {string} message The error message to set.
 */
caterpillar_.setError = function(message) {
  chrome.runtime.lastError = { 'message': message };
};

// Disable web features that are disabled in Chrome Apps. See
// https://developer.chrome.com/apps/app_deprecated. These functions intend to
// match the behaviour of Chrome Apps when the disabled functions are called.
var logNotAvailable = function(name) {
  throw new Error(name + '() is not available in converted apps.');
}
self.alert = logNotAvailable.bind(null, 'alert');
self.confirm = logNotAvailable.bind(null, 'confirm');
self.prompt = logNotAvailable.bind(null, 'prompt');
self.showModalDialog = logNotAvailable.bind(null, 'showModalDialog');
if ('document' in self) {
  document.cookie = '';
  document.close = logNotAvailable.bind(null, 'document.close');
  document.open = logNotAvailable.bind(null, 'document.open');
  document.write = logNotAvailable.bind(null, 'document.write');

  // Disable user text selection.
  document.addEventListener('selectstart', function() { return false; });
}
delete self.localStorage;

}).call(this);
