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
 * Common utilities and types for Caterpillar.
 *
 * Must be included before any Caterpillar polyfills.
 */

'use strict';

// Set up a namespace if one doesn't already exist.
if (!('chrome' in self))
  self.chrome = {};

if (!chrome.caterpillar)
  chrome.caterpillar = {};

// We need the chrome.runtime namespace to store errors in.
if (!chrome.runtime)
  chrome.runtime = { lastError: null };

// Stub out chrome.app.runtime.onLaunched.addListener. All Chrome Apps call this
// method to launch the main window. Stubbing it means that background scripts
// that launch the main window can be re-used elsewhere without causing script
// errors.
chrome.app = {
  runtime: {
    onLaunched: {
      addListener: function() {},
    }
  }
};

(function() {

/**
 * Sets an error message in chrome.runtime.lastError.
 *
 * @param {string} message The error message to set.
 */
chrome.caterpillar.setError = function(message) {
  chrome.runtime.lastError = { 'message': message };
};

}).call(this);
